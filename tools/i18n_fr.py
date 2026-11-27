"""Kept for older notes: the engine is now tools/i18n.py (all languages).
python3 -I tools/i18n_fr.py <build|extract|report|csv> [root]  =  tools/i18n.py with locale fr-CA."""
import os, sys, runpy
args = sys.argv[1:] or ['build']
sys.argv = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'i18n.py')] + (args if args[0] == 'build' else [args[0], 'fr-CA'] + args[1:])
runpy.run_path(sys.argv[0], run_name='__main__')
