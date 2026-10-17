"""Run B01's inherited regression suites, plus C01-specific checks, on C01's frozen and ZIP-extracted files.

Reuses team-work/member-1/implementation/final-sprint fixtures read-only; logs go to this folder.
Run: ./team-work/run-python.sh team-work/member-2/implementation/C01/verify_c01.py
"""
from pathlib import Path
import ast, hashlib, io, json, sys, types, unittest, zipfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
PREV = ROOT / 'team-work/member-1/implementation/final-sprint'
sys.path.insert(0, str(PREV))
sys.path.insert(0, str(BASE))
v = types.ModuleType('c01_verifier'); v.__file__ = str(PREV / 'verify_candidates.py'); v.OUTPUT = BASE
exec(compile((PREV / 'verify_candidates.py').read_text().replace(
    "(BASE/f'verification-{name}.log')", "(OUTPUT/f'verification-{name}.log')"), v.__file__, 'exec'), v.__dict__)
import test_sprint as extra
import test_two_roads as road
import test_c01 as c01tests

SOURCE = ROOT / 'team-work/member-2/bots/C01/v001/agent.py'
ARCHIVE = ROOT / 'team-work/member-2/artifacts/C01-v001.zip'
EXTRACT = ROOT / 'shared-local/c01-v001-package-check'
PRESERVED = {
    'team-work/member-1/bots/B01/v004/agent.py': 'a0ed4450b3aa23eff97ab44fbe185e2d089ddc9516a1703e4b483389ed8ff2fb',
    'team-work/member-1/bots/B01/v005/agent.py': '63ab59c8b302a863dab38e07c461338be7cbbbe91b254b96fe359c8786fb9bd5',
    'team-work/member-3/bots/B05/v004/agent.py': '8226e2c978cd6ec48fee2939dd4ccf021acb64e131b87bc71ddfcd29e0d05cbf',
    'shared-local/organizer-kit/examples/f_agent.py': '72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613',
}
SPRINT = ['test_goal_reconsiders_changed_hand_instead_of_stale_family',
          'test_reordered_opening_indices_and_observation_immutability',
          'test_trade_retains_monotone_certificate_and_no_reexport',
          'test_reordered_rich_turn_roots_legal_and_nonmutating']


def main():
    data = SOURCE.read_bytes()
    with zipfile.ZipFile(ARCHIVE, 'w') as z:
        info = zipfile.ZipInfo('agent.py', date_time=(2026, 10, 17, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o644 << 16
        z.writestr(info, data)
    EXTRACT.mkdir(exist_ok=True)
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.namelist() == ['agent.py'] and z.testzip() is None and z.read('agent.py') == data
        z.extractall(EXTRACT)
    records = {}
    for name, path in [('frozen', SOURCE), ('zip-extracted', EXTRACT / 'agent.py')]:
        records[name] = v.run('c01-' + name, path)
        m = v.r.load('c01_' + name.replace('-', '_'), path)
        extra.mods = {'menu': m, 'combined': m, 'search': m}; road.M = m; c01tests.M = m
        suite = unittest.TestSuite(extra.SprintTests(x) for x in SPRINT)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(road))
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(c01tests))
        stream = io.StringIO(); result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        (BASE / f'verification-extra-c01-{name}.log').write_text(stream.getvalue())
        assert result.wasSuccessful(), stream.getvalue()
        assert records[name]['terminal_passed'] and records[name]['economic_passed']
        records[name].update(extra_methods=result.testsRun, extra_passed=True)
    imports = []
    for n in ast.walk(ast.parse(data)):
        if isinstance(n, ast.Import): imports.extend(a.name for a in n.names)
        if isinstance(n, ast.ImportFrom): imports.append(n.module)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            assert n.func.id not in ('open', 'eval', 'exec', 'compile', '__import__', 'print')
    assert all(x in ('math', 'time', 'random') or x.startswith('catanatron.') for x in imports)
    for rel, sha in PRESERVED.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == sha, rel
    out = {'agent_sha256': hashlib.sha256(data).hexdigest(),
           'zip_sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
           'zip_members': ['agent.py'], 'zip_bytes_equal_source': True,
           'preserved_sources_unchanged': list(PRESERVED), 'imports': sorted(set(imports)),
           'verification': records}
    (BASE / 'verification.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
