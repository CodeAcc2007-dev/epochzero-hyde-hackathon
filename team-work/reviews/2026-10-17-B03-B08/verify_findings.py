"""Reproduce frozen-version review findings, NOT passing tests of fixed bots.

Constructed/counterfactual engine states; no full reachable-history claim.
No production source is changed. Run with the shared launcher from repo root.
Requires the pinned Member2 snapshot (see README.md).
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT = ROOT/'shared-local/review-B03-B08-20261017/team-work/member-2/bots'
sys.path.insert(0,str(ROOT/'team-work/member-3/implementation'))
import test_policies as f
from catan_kit.obs import Obs
from catanatron.models.enums import ActionType as AT


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def paths():
    return {**{b:ROOT/f'team-work/member-1/bots/{b}/v001/agent.py' for b in ('B01','B02')},**{b:SNAPSHOT/b/'v002/agent.py' for b in ('B03','B04')},
            **{b:ROOT/f'team-work/member-3/bots/{b}/v003/agent.py' for b in ('B05','B06')},
            **{b:ROOT/f'team-work/member-4/bots/{b}/v001/agent.py' for b in ('B07','B08')}}


def main():
    modules={b:load('review_'+b,p) for b,p in paths().items()}
    result={'scope':'Constructed states and source-contract probes, not strength tests or full reachable histories',
            'entrypoint_sha256':{b:hashlib.sha256(p.read_bytes()).hexdigest() for b,p in paths().items()},'findings':{}}
    out=result['findings']
    # Actual invariant-preserving nine-VP position; a legal settlement wins.
    g,c=f.near_win();g=f.road_settlement_fixture(g,c)
    for a in g.playable_actions:
        if a.action_type!=AT.BUILD_ROAD:continue
        h=g.copy();h.execute(a)
        if any(b.action_type==AT.BUILD_SETTLEMENT for b in h.playable_actions):
            g=h;break
    f.set_hand(g,c,(1,1,1,1,0));f.invariant(g)
    winning=next(a for a in g.playable_actions if a.action_type==AT.BUILD_SETTLEMENT)
    h=g.copy();h.execute(winning);f.invariant(h);assert h.winning_color()==c
    choices={}
    for b in ('B01','B02','B05','B06','B07','B08'):
        obs=Obs(g,c);obs.cpu_left=.0009
        action=g.playable_actions[modules[b].Agent().decide(obs,g.playable_actions)]
        assert action.action_type==AT.END_TURN
        choices[b]=str(action)
    out['COMMON-01']={'cpu_left':.0009,'actual_vp':9,'winning_action':str(winning),'chosen':choices}
    # Retained city goal rejects a trade which enables an immediate Road-bonus win.
    blocked={}
    for b in ('B01','B02'):
        g,c=f.near_win();k=f.key(g,c)
        g.state.player_state[k+'_VICTORY_POINT_IN_HAND']-=1
        g.state.player_state[k+'_ACTUAL_VICTORY_POINTS']-=1
        g.state.development_listdeck.append('VICTORY_POINT')
        f.extend_road(g,c,4);f.set_hand(g,c,(0,1,0,2,4));f.invariant(g)
        assert g.winning_color() is None
        ctx=modules[b].EconomyContext(g,c,b=='B02')
        chain=None
        for a in g.playable_actions:
            if a.action_type!=AT.MARITIME_TRADE:continue
            h=g.copy();h.execute(a)
            for road in h.playable_actions:
                if road.action_type!=AT.BUILD_ROAD:continue
                end=h.copy();end.execute(road)
                if end.winning_color()==c:
                    f.invariant(end);chain=(a,road);break
            if chain:break
        assert chain is not None
        rejected=ctx.action_value(g,chain[0])
        assert rejected[0]==-float('inf') and rejected[1] is None
        obs=Obs(g,c);obs.cpu_left=1
        chosen=g.playable_actions[modules[b].Agent().decide(obs,g.playable_actions)]
        assert chosen.action_type==AT.BUILD_CITY
        end=g.copy();end.execute(chosen);assert end.winning_color() is None
        blocked[b]={'actual_vp':8,'hand':[0,1,0,2,4],'retained_family':ctx.family,
                    'winning_chain':[str(a) for a in chain],'trade_rejected':True,
                    'chosen_nonterminal':str(chosen)}
    out['M1-GOAL-TERMINAL']=blocked
    # Opponent's existing road network already reaches a buildable node.
    g,c=f.fresh();enemy=next(x for x in g.state.colors if x!=c)
    f.extend_road(g,enemy,6);f.invariant(g)
    reach=modules['B03'].Agent()._opp_reach(Obs(g,c),c)
    missed=sorted(set(g.state.board.buildable_node_ids(enemy))-reach)
    assert missed==[39]
    out['B03-01']={'existing_enemy_road_length':6,'legal_enemy_settlement_nodes_missing_from_reach':missed}
    # Search legal road prefixes, then identify a new port at the LOWER edge endpoint.
    g,c=f.fresh();front=[(g,[])];found=None
    for depth in range(5):
        nxt=[]
        for g,history in front:
            f.set_hand(g,c,(1,1,0,0,0))
            ports=set().union(*g.state.board.map.port_nodes.values())
            connected=set().union(*g.state.board.connected_components[c])
            for a in g.playable_actions:
                if a.action_type!=AT.BUILD_ROAD:continue
                if a.value[1] in connected and a.value[0] not in connected and a.value[0] in ports:
                    found=(g,c,a,history,connected);break
                h=g.copy();h.execute(a);nxt.append((h,history+[list(a.value)]))
            if found:break
        if found:break
        front=nxt[:500]
    assert found is not None
    g,c,a,history,connected=found;f.invariant(g)
    agent=modules['B04'].Agent();seen=[]
    agent._justified_port_value=lambda obs,me,node,child,scale:(seen.append(node) or 0)
    h=g.copy();h.execute(a);agent._port_bonus(Obs(g,c),c,a,h)
    assert seen==[a.value[1]] and a.value[0] not in connected
    out['B04-01']={'legal_road_prefix':history,'legal_next_edge':list(a.value),'new_port_node':a.value[0],'node_scored_as_far':seen[0]}
    # Exact 5/36 probability fails the rounded-up advertised threshold; zero production still earns credit.
    agent=modules['B04'].Agent()
    resource,nodes=next((r,n) for r,n in g.state.board.map.port_nodes.items() if r is not None)
    node=next(iter(nodes));observed={}
    for rate in (0.0,5/36,.14):
        agent._my_production=lambda game,me,rate=rate:{resource:rate}
        observed[str(rate)]=agent._justified_port_value(Obs(g,c),c,node,g,3e6)
    assert observed[str(0.0)]==300000 and observed[str(5/36)]==300000 and observed[str(.14)]==3e6
    out['B04-02']={'resource':resource,'bonus_by_production':observed,'threshold':modules['B04'].PROBA_6}
    # Current direct-affordability misses an exact bank-trade enabler.
    g,c=f.fresh();enemy=next(x for x in g.state.colors if x!=c)
    for _ in range(2):f.add_settlement(g,enemy)
    for _ in range(3):f.upgrade(g,enemy)
    ek=f.key(g,enemy)
    for _ in range(3):g.state.development_listdeck.remove('KNIGHT')
    g.state.player_state[ek+'_PLAYED_KNIGHT']=3
    g.state.player_state[ek+'_HAS_ARMY']=True
    g.state.player_state[ek+'_VICTORY_POINTS']+=2
    g.state.player_state[ek+'_ACTUAL_VICTORY_POINTS']+=2
    f.set_hand(g,enemy,(4,0,0,2,2));f.phase(g,enemy,True);f.invariant(g)
    from member3_core import Context,hand
    ctx=Context(g,c,True);risk=ctx.threat(g,hand(g.state,ctx.ekey));assert risk==0
    completion=None
    for a in g.playable_actions:
        if a.action_type!=AT.MARITIME_TRADE:continue
        h=g.copy();h.execute(a)
        city=next((b for b in h.playable_actions if b.action_type==AT.BUILD_CITY),None)
        if city:
            h.execute(city);f.invariant(h)
            if h.winning_color()==enemy:completion=[str(a),str(city)];break
    assert completion is not None
    out['B06-01']={'enemy_public_vp':9,'enemy_hand':[4,0,0,2,2],'threat_score':risk,'winning_postroll_chain':completion,'certainty':'Post-roll constructed state; no claim about the next random roll'}
    # Reply cap allocates just one slot to YOP when other dev types are present.
    g,c=f.fresh();enemy=next(x for x in g.state.colors if x!=c)
    for dev in ('KNIGHT','MONOPOLY','ROAD_BUILDING','YEAR_OF_PLENTY'):f.dev(g,enemy,dev,old=True)
    f.phase(g,enemy,False);f.invariant(g)
    order={AT.PLAY_KNIGHT_CARD:0,AT.PLAY_MONOPOLY:1,AT.PLAY_ROAD_BUILDING:2,AT.PLAY_YEAR_OF_PLENTY:3}
    replies=sorted((a for a in g.playable_actions if a.action_type in order),key=lambda a:(order[a.action_type],repr(a.value)))
    capped=replies[:8]
    assert sum(a.action_type==AT.PLAY_YEAR_OF_PLENTY for a in capped)==1
    out['B07-01']={'legal_reply_count':len(replies),'selected_first_eight':[str(a) for a in capped],'omitted_yop_count':sum(a.action_type==AT.PLAY_YEAR_OF_PLENTY for a in replies[8:]),'scope':'Source-exact truncation policy probe; not a proven lost game'}
    # Army route needs a newly bought knight but records no turn delay.
    g,c=f.fresh();k=f.key(g,c)
    for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
    g.state.player_state[k+'_PLAYED_KNIGHT']=2
    f.set_hand(g,c,(0,0,2,2,2));f.invariant(g)
    ctx=modules['B08'].RouteContext(g,c)
    army=next(p for p in ctx.plans(g,tuple((0,0,2,2,2))) if p[0]=='army')
    assert army[-1]==0 and g.state.player_state[k+'_KNIGHT_IN_HAND']==0
    buy=next(a for a in g.playable_actions if a.action_type==AT.BUY_DEVELOPMENT_CARD)
    from catanatron.models.enums import ActionRecord
    h=g.copy();h.execute(buy,action_record=ActionRecord(buy,'KNIGHT'));f.invariant(h)
    assert not any(a.action_type==AT.PLAY_KNIGHT_CARD for a in h.playable_actions)
    out['B08-01']={'army_plan':army,'new_knight_playable_this_turn':False,'scope':'Delay-model defect, not an illegal move emitted by the bot'}
    # The Member2 exception wrapper hides failures from harness error counters.
    hidden={}
    for b in ('B03','B04'):
        g,c=f.fresh();f.set_hand(g,c,(4,4,1,1,1));agent=modules[b].Agent()
        def fail(*args):raise RuntimeError('injected review sentinel')
        agent._score=fail
        obs=Obs(g,c);obs.cpu_left=1
        chosen=g.playable_actions[agent.decide(obs,g.playable_actions)]
        assert chosen.action_type==AT.END_TURN
        hidden[b]=str(chosen)
    out['M2-OBSERVABILITY']={'injected_score_exception_returned_normally':hidden,'scope':'Failure-injection observability probe; does not establish faults in historical games'}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
