"""Apply existing semantic cases to new standalone modules; external diagnostics only."""
import hashlib, importlib.util, io, json, sys, time, unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE))
import test_round2 as r
from catan_kit.obs import Obs
from catanatron.models.enums import ActionType as AT
from unittest.mock import patch


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
    new3=r.NEW['B05'];new4=r.NEW['B08']
    a=load('adapted_member3',ROOT/'team-work/member-3/implementation/test_policies.py')
    a.Policy=new3.Policy;a.Context=new3.Context
    def road_then_win(self):
        g,c=a.near_win();g=a.road_settlement_fixture(g,c);a.set_hand(g,c,(2,2,1,1,0))
        self.assertFalse(any(x.action_type==AT.BUILD_SETTLEMENT for x in g.playable_actions))
        move=a.choose(g,c,'beam');self.assertEqual(move.action_type,AT.BUILD_ROAD);g.execute(move)
        if g.winning_color()!=c:
            move=a.choose(g,c,'beam');g.execute(move)
        a.invariant(g);self.assertEqual(g.winning_color(),c)
    a.PolicyTests.test_road_then_settlement_terminal=road_then_win
    b=load('adapted_member4',ROOT/'team-work/member-4/implementation/test_member4.py')
    b.Member4Policy=new4.Member4Policy;b.RouteContext=new4.RouteContext;b.Context=new4.Context
    # The new selector deliberately omits zero-theft Monopoly choices: the
    # existing fixture has two nonempty types, so two replies replace five.
    original_equal=unittest.TestCase.assertEqual
    class NewEngineTests(b.EngineTests):
        def test_hidden_monopoly_reply_has_observable_model_effect(self):
            g,c=b.fixture.fresh();e=next(x for x in g.state.colors if x!=c)
            b.fixture.set_hand(g,c,(0,0,0,4,3));b.fixture.dev(g,e,'MONOPOLY',old=False)
            ctx=b.Context(g,c,True);agent=b.Member4Policy('belief')
            end=next(x for x in g.playable_actions if x.action_type==AT.END_TURN)
            out=agent.forecast_end(g,end,ctx,time.process_time()+1)
            self.assertLess(agent.opponent_reply(out,ctx,time.process_time()+1),ctx.value(out));self.assertEqual(agent.reply_nodes,2)
        def test_standalone_modules_load_without_helper_imports(self):
            for bot in ('B07','B08'):
                m=r.NEW[bot];g,c=r.f.fresh();obs=Obs(g,c);obs.cpu_left=.3
                idx=m.Agent().decide(obs,g.playable_actions);self.assertIs(type(idx),int)
                self.assertTrue(0<=idx<len(g.playable_actions))
                source=r.candidate(bot).read_text();self.assertNotIn('from public_context import',source)
                self.assertNotIn('from round2_math import',source)
    suite=unittest.TestSuite()
    # The old module-identity assertion is about preserved parents and is
    # verified separately. All other Member3 policy cases load the new code.
    for name in unittest.defaultTestLoader.getTestCaseNames(a.PolicyTests):
        if name!='test_runtime_modules_identical':suite.addTest(a.PolicyTests(name))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(NewEngineTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(b.RouteMathTests))
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (ROOT/'shared-local/round2-adapted-contract-tests.log').write_text(stream.getvalue())
    print(stream.getvalue())
    if not result.wasSuccessful():raise SystemExit(1)
    record={'new_regression_methods':18,'adapted_existing_methods':result.testsRun,
            'adaptation':'Existing Member3 PolicyTests use new Policy/Context; parent-file identity excluded. Member4 Engine/RouteMath cases use new standalone classes; zero-theft Monopoly expected count updated from 5 to 2, standalone loading targets new files. Road-to-settlement fixture accepts an earlier Road-bonus win and still asserts the exact engine winner.',
            'artifacts':{bot:{'path':str(r.candidate(bot).relative_to(ROOT)),'sha256':hashlib.sha256(r.candidate(bot).read_bytes()).hexdigest()} for bot in r.NEW}}
    for member in (3,4):
        (ROOT/f'team-work/member-{member}/implementation/round-2/semantic-verification.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':main()
