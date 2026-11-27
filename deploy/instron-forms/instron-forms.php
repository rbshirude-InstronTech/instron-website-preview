<?php
/**
 * Plugin Name: Instron Technologies Forms
 * Description: Website enquiry and careers forms that send directly by email (authenticated SMTP) and create an ERPNext lead. No third-party form service.
 * Version:     1.0.0
 * Author:      Instron Technologies
 * License:     Proprietary
 * Requires PHP: 7.4
 *
 * Configuration lives in wp-config.php (never in this file or in Git):
 *
 *   // Recipients
 *   define('INSTRON_FORMS_SALES_TO',   'sales@instrontechnologies.com');
 *   define('INSTRON_FORMS_CAREERS_TO', 'careers@instrontechnologies.com');
 *   define('INSTRON_FORMS_FROM',       'website@instrontechnologies.com'); // a real Workspace mailbox or alias
 *   define('INSTRON_FORMS_ACK',        true);  // short acknowledgement to the visitor
 *
 *   // Authenticated SMTP (Google Workspace). Leave undefined to use the server's default mailer.
 *   define('INSTRON_SMTP_HOST', 'smtp.gmail.com');
 *   define('INSTRON_SMTP_PORT', 587);
 *   define('INSTRON_SMTP_USER', 'website@instrontechnologies.com');
 *   define('INSTRON_SMTP_PASS', 'app-password-here');
 *
 *   // ERPNext lead (optional). Use an API user that may only create Leads.
 *   define('INSTRON_ERPNEXT_URL',    'https://erp.example.com');
 *   define('INSTRON_ERPNEXT_KEY',    '...');
 *   define('INSTRON_ERPNEXT_SECRET', '...');
 *
 * Endpoints:
 *   POST /wp-json/instron/v1/enquiry      (JSON or form data)
 *   POST /wp-json/instron/v1/application  (multipart form data, optional CV upload)
 *
 * Privacy: submissions are not stored in the WordPress database. They go to the mailbox and,
 * for enquiries, to ERPNext. The visitor IP is kept only as a salted hash in a one-hour
 * transient for rate limiting.
 */

if (!defined('ABSPATH')) {
    exit;
}

const INSTRON_FORMS_VERSION = '1.0.0';
const INSTRON_FORMS_RATE_LIMIT = 5;          // submissions per IP per hour, per form
const INSTRON_FORMS_MIN_SECONDS = 3;         // faster than this is treated as a bot
const INSTRON_FORMS_CV_MAX_BYTES = 5242880;  // 5 MB

/* ------------------------------------------------------------------ config */

function instron_forms_cfg($name, $default = null)
{
    return defined($name) ? constant($name) : $default;
}

/* ------------------------------------------------------------------- SMTP */

add_action('phpmailer_init', function ($mailer) {
    $host = instron_forms_cfg('INSTRON_SMTP_HOST');
    if (!$host) {
        return;
    }
    $mailer->isSMTP();
    $mailer->Host       = $host;
    $mailer->Port       = (int) instron_forms_cfg('INSTRON_SMTP_PORT', 587);
    $mailer->SMTPAuth   = true;
    $mailer->SMTPSecure = ((int) $mailer->Port === 465) ? 'ssl' : 'tls';
    $mailer->Username   = instron_forms_cfg('INSTRON_SMTP_USER', '');
    $mailer->Password   = instron_forms_cfg('INSTRON_SMTP_PASS', '');
});

/* ------------------------------------------------------------- REST routes */

add_action('rest_api_init', function () {
    register_rest_route('instron/v1', '/enquiry', array(
        'methods'             => 'POST',
        'callback'            => 'instron_forms_enquiry',
        'permission_callback' => '__return_true',
    ));
    register_rest_route('instron/v1', '/application', array(
        'methods'             => 'POST',
        'callback'            => 'instron_forms_application',
        'permission_callback' => '__return_true',
    ));
});

/* ---------------------------------------------------------------- helpers */

function instron_forms_reply($ok, $message, $status = 200)
{
    return new WP_REST_Response(array('ok' => (bool) $ok, 'message' => $message), $status);
}

/** Single-line text: strip tags and control characters, collapse spaces, cut to length. */
function instron_forms_line($value, $max)
{
    $value = wp_strip_all_tags((string) $value);
    $value = preg_replace('/[\x00-\x1F\x7F]+/u', ' ', $value);
    $value = trim(preg_replace('/\s+/u', ' ', $value));
    return mb_substr($value, 0, $max);
}

/** Multi-line text: strip tags, keep line breaks, cut to length. */
function instron_forms_text($value, $max)
{
    $value = wp_strip_all_tags((string) $value);
    $value = str_replace(array("\r\n", "\r"), "\n", $value);
    $value = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]+/u', '', $value);
    return mb_substr(trim($value), 0, $max);
}

/** Request must come from this site (Origin, or Referer when Origin is absent). */
function instron_forms_same_origin(WP_REST_Request $req)
{
    $site = wp_parse_url(home_url(), PHP_URL_HOST);
    $from = $req->get_header('origin') ?: $req->get_header('referer');
    if (!$from) {
        return false;
    }
    $host = wp_parse_url($from, PHP_URL_HOST);
    return $host && strtolower($host) === strtolower($site);
}

/** Honeypot field must be empty and the form must not be submitted implausibly fast. */
function instron_forms_is_bot(array $p)
{
    if (!empty($p['website'])) {
        return true;
    }
    $ts = isset($p['_ts']) ? (int) $p['_ts'] : 0;   // milliseconds since epoch, set by the form script
    if ($ts > 0 && (microtime(true) * 1000 - $ts) < INSTRON_FORMS_MIN_SECONDS * 1000) {
        return true;
    }
    return false;
}

/** True while this IP is under the hourly limit for the given form; counts the attempt. */
function instron_forms_rate_ok($form)
{
    $ip  = isset($_SERVER['REMOTE_ADDR']) ? (string) $_SERVER['REMOTE_ADDR'] : 'unknown';
    $key = 'instron_rl_' . $form . '_' . substr(hash_hmac('sha256', $ip, wp_salt('nonce')), 0, 24);
    $n   = (int) get_transient($key);
    if ($n >= INSTRON_FORMS_RATE_LIMIT) {
        return false;
    }
    set_transient($key, $n + 1, HOUR_IN_SECONDS);
    return true;
}

function instron_forms_params(WP_REST_Request $req)
{
    $json = $req->get_json_params();
    return is_array($json) && $json ? $json : $req->get_body_params();
}

function instron_forms_mail($to, $subject, $body, $reply_to = '', array $attachments = array())
{
    $headers = array('Content-Type: text/plain; charset=UTF-8');
    $from = instron_forms_cfg('INSTRON_FORMS_FROM');
    if ($from) {
        $headers[] = 'From: Instron Technologies website <' . $from . '>';
    }
    if ($reply_to && is_email($reply_to)) {
        $headers[] = 'Reply-To: ' . $reply_to;
    }
    return wp_mail($to, $subject, $body, $headers, $attachments);
}

function instron_forms_ack($to, $subject, $body)
{
    if (!instron_forms_cfg('INSTRON_FORMS_ACK', true)) {
        return;
    }
    instron_forms_mail($to, $subject, $body);
}

/** Create an ERPNext Lead. Returns true on success; failures are logged and never block the email. */
function instron_forms_erpnext_lead(array $f)
{
    $url    = instron_forms_cfg('INSTRON_ERPNEXT_URL');
    $key    = instron_forms_cfg('INSTRON_ERPNEXT_KEY');
    $secret = instron_forms_cfg('INSTRON_ERPNEXT_SECRET');
    if (!$url || !$key || !$secret) {
        return false;
    }
    $notes = "Website enquiry\n"
        . 'Enquiry type: ' . $f['type'] . "\n"
        . 'Project stage: ' . $f['stage'] . "\n"
        . 'Country: ' . $f['country'] . "\n\n"
        . $f['challenge'];
    $lead = array(
        'lead_name'    => $f['name'],
        'first_name'   => $f['name'],
        'company_name' => $f['company'],
        'email_id'     => $f['email'],
        'mobile_no'    => $f['phone'],
        'source'       => 'Website',
        'notes'        => array(array('note' => nl2br(esc_html($notes)))),
    );
    $post = function (array $doc) use ($url, $key, $secret) {
        return wp_remote_post(untrailingslashit($url) . '/api/resource/Lead', array(
            'timeout' => 10,
            'headers' => array(
                'Authorization' => 'token ' . $key . ':' . $secret,
                'Content-Type'  => 'application/json',
                'Accept'        => 'application/json',
            ),
            'body'    => wp_json_encode($doc),
        ));
    };
    $res  = $post($lead);
    $code = is_wp_error($res) ? 0 : (int) wp_remote_retrieve_response_code($res);
    if ($code >= 400 && $code < 500 && $code !== 401 && $code !== 403) {
        // Older or customised ERPNext (no notes table, stricter phone field): retry with core fields only.
        $res  = $post(array(
            'lead_name'    => $f['name'],
            'first_name'   => $f['name'],
            'company_name' => $f['company'],
            'email_id'     => $f['email'],
            'source'       => 'Website',
        ));
        $code = is_wp_error($res) ? 0 : (int) wp_remote_retrieve_response_code($res);
    }
    if ($code < 200 || $code >= 300) {
        $why = is_wp_error($res) ? $res->get_error_message() : ('HTTP ' . $code);
        error_log('[instron-forms] ERPNext lead not created: ' . $why);
        return false;
    }
    return true;
}

/* ---------------------------------------------------------------- enquiry */

function instron_forms_enquiry(WP_REST_Request $req)
{
    if (!instron_forms_same_origin($req)) {
        return instron_forms_reply(false, 'Please send the enquiry from the website form.', 403);
    }
    $p = instron_forms_params($req);
    if (instron_forms_is_bot($p)) {
        return instron_forms_reply(true, 'Thank you. Your enquiry has been sent.');   // silent drop
    }
    if (!instron_forms_rate_ok('enquiry')) {
        return instron_forms_reply(false, 'Too many enquiries from this connection. Please email sales@instrontechnologies.com.', 429);
    }

    $f = array(
        'name'      => instron_forms_line($p['name'] ?? '', 100),
        'email'     => sanitize_email($p['email'] ?? ''),
        'company'   => instron_forms_line($p['company'] ?? '', 160),
        'country'   => instron_forms_line($p['country'] ?? '', 100),
        'type'      => instron_forms_line($p['type'] ?? '', 80),
        'stage'     => instron_forms_line($p['stage'] ?? '', 80),
        'phone'     => instron_forms_line($p['phone'] ?? '', 50),
        'challenge' => instron_forms_text($p['challenge'] ?? '', 3000),
        'page'      => esc_url_raw(instron_forms_line($p['page'] ?? '', 300)),
    );

    $missing = array();
    foreach (array('name' => 'name', 'company' => 'company', 'country' => 'country') as $k => $label) {
        if ($f[$k] === '') {
            $missing[] = $label;
        }
    }
    if (!is_email($f['email'])) {
        $missing[] = 'a valid email address';
    }
    if (mb_strlen($f['challenge']) < 10) {
        $missing[] = 'a short description of the engineering question';
    }
    if ($missing) {
        return instron_forms_reply(false, 'Please add ' . implode(', ', $missing) . '.', 422);
    }

    $subject = 'Website enquiry: ' . $f['company'] . ' (' . $f['country'] . ')';
    $body = "New enquiry from the Instron Technologies website\n\n"
        . 'Name: ' . $f['name'] . "\n"
        . 'Email: ' . $f['email'] . "\n"
        . 'Company: ' . $f['company'] . "\n"
        . 'Country: ' . $f['country'] . "\n"
        . 'Phone: ' . ($f['phone'] ?: 'not given') . "\n"
        . 'Enquiry type: ' . ($f['type'] ?: 'not given') . "\n"
        . 'Project stage: ' . ($f['stage'] ?: 'not given') . "\n"
        . 'Sent from page: ' . ($f['page'] ?: 'not given') . "\n\n"
        . "Engineering question:\n" . $f['challenge'] . "\n";

    $lead = instron_forms_erpnext_lead($f);
    $body .= "\nERPNext lead: " . ($lead ? 'created' : 'not created (create it manually)') . "\n";

    $to = instron_forms_cfg('INSTRON_FORMS_SALES_TO', 'sales@instrontechnologies.com');
    if (!instron_forms_mail($to, $subject, $body, $f['email'])) {
        error_log('[instron-forms] enquiry email failed');
        return instron_forms_reply(false, 'The enquiry could not be sent. Please email sales@instrontechnologies.com.', 500);
    }

    instron_forms_ack($f['email'], 'We received your enquiry | Instron Technologies',
        "Hello " . $f['name'] . ",\n\n"
        . "Thank you for contacting Instron Technologies. An engineer will review your enquiry and reply by email.\n\n"
        . "If you need to add drawings or details, reply to sales@instrontechnologies.com.\n\n"
        . "Instron Technologies\nwww.instrontechnologies.com\n");

    return instron_forms_reply(true, 'Thank you. Your enquiry has been sent, and an engineer will reply by email.');
}

/* ------------------------------------------------------------ application */

function instron_forms_application(WP_REST_Request $req)
{
    if (!instron_forms_same_origin($req)) {
        return instron_forms_reply(false, 'Please apply from the website form.', 403);
    }
    $p = $req->get_body_params();
    if (instron_forms_is_bot($p)) {
        return instron_forms_reply(true, 'Thank you. Your application has been sent.');
    }
    if (!instron_forms_rate_ok('application')) {
        return instron_forms_reply(false, 'Too many applications from this connection. Please email careers@instrontechnologies.com.', 429);
    }

    $f = array(
        'name'       => instron_forms_line($p['name'] ?? '', 100),
        'email'      => sanitize_email($p['email'] ?? ''),
        'phone'      => instron_forms_line($p['phone'] ?? '', 50),
        'location'   => instron_forms_line($p['location'] ?? '', 100),
        'discipline' => instron_forms_line($p['discipline'] ?? '', 120),
        'message'    => instron_forms_text($p['message'] ?? '', 3000),
    );
    if ($f['name'] === '' || !is_email($f['email'])) {
        return instron_forms_reply(false, 'Please add your name and a valid email address.', 422);
    }

    $attachments = array();
    $files = $req->get_file_params();
    if (!empty($files['cv']) && (int) $files['cv']['error'] !== UPLOAD_ERR_NO_FILE) {
        $cv = $files['cv'];
        if ((int) $cv['error'] !== UPLOAD_ERR_OK || !is_uploaded_file($cv['tmp_name'])) {
            return instron_forms_reply(false, 'The CV could not be uploaded. Please try again.', 422);
        }
        if ((int) $cv['size'] > INSTRON_FORMS_CV_MAX_BYTES) {
            return instron_forms_reply(false, 'The CV must be 5 MB or smaller.', 422);
        }
        $allowed = array(
            'pdf'  => 'application/pdf',
            'doc'  => 'application/msword',
            'docx' => 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        );
        $ext  = strtolower(pathinfo((string) $cv['name'], PATHINFO_EXTENSION));
        $mime = function_exists('finfo_open') ? finfo_file(finfo_open(FILEINFO_MIME_TYPE), $cv['tmp_name']) : '';
        $docx_zip = ($ext === 'docx' && $mime === 'application/zip');
        if (!isset($allowed[$ext]) || ($mime !== $allowed[$ext] && !$docx_zip)) {
            return instron_forms_reply(false, 'Please upload the CV as PDF, DOC or DOCX.', 422);
        }
        // Copy to a temporary file with a safe name; removed right after sending.
        $safe = sanitize_file_name(($f['name'] ?: 'applicant') . '-cv.' . $ext);
        $tmp  = trailingslashit(get_temp_dir()) . wp_generate_password(12, false) . '-' . $safe;
        if (!copy($cv['tmp_name'], $tmp)) {
            return instron_forms_reply(false, 'The CV could not be processed. Please email careers@instrontechnologies.com.', 500);
        }
        $attachments[] = $tmp;
    }

    $subject = 'Website application: ' . $f['name'] . ($f['discipline'] ? ' (' . $f['discipline'] . ')' : '');
    $body = "New application from the Instron Technologies careers page\n\n"
        . 'Name: ' . $f['name'] . "\n"
        . 'Email: ' . $f['email'] . "\n"
        . 'Phone: ' . ($f['phone'] ?: 'not given') . "\n"
        . 'Location: ' . ($f['location'] ?: 'not given') . "\n"
        . 'Discipline: ' . ($f['discipline'] ?: 'not given') . "\n"
        . 'CV attached: ' . ($attachments ? 'yes' : 'no') . "\n\n"
        . "Message:\n" . ($f['message'] ?: '(none)') . "\n\n"
        . "Retention: delete unsuccessful applications after 12 months.\n";

    $to   = instron_forms_cfg('INSTRON_FORMS_CAREERS_TO', 'careers@instrontechnologies.com');
    $sent = instron_forms_mail($to, $subject, $body, $f['email'], $attachments);
    foreach ($attachments as $a) {
        @unlink($a);
    }
    if (!$sent) {
        error_log('[instron-forms] application email failed');
        return instron_forms_reply(false, 'The application could not be sent. Please email careers@instrontechnologies.com.', 500);
    }

    instron_forms_ack($f['email'], 'We received your application | Instron Technologies',
        "Hello " . $f['name'] . ",\n\n"
        . "Thank you for applying to Instron Technologies. Our team will review your application and contact you if there is a suitable opening.\n\n"
        . "Instron Technologies\nwww.instrontechnologies.com\n");

    return instron_forms_reply(true, 'Thank you. Your application has been sent.');
}

/* ------------------------------------------------------- front-end script */

add_action('wp_enqueue_scripts', function () {
    wp_enqueue_script('instron-forms', plugins_url('instron-forms.js', __FILE__), array(), INSTRON_FORMS_VERSION, true);
    wp_localize_script('instron-forms', 'InstronForms', array(
        'enquiry'     => esc_url_raw(rest_url('instron/v1/enquiry')),
        'application' => esc_url_raw(rest_url('instron/v1/application')),
    ));
});
