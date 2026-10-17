def terminal_two_roads(obs, actions, deadline):
    """Certify at most an enabling action plus two legal roads, never a guess.

    Public/own state only. At most80 copied executions and12 enabling roots;
    elapsed CPU cutoff means unsearched. All child actions come from the engine.
    Does not continue through rolls, draws, steals or other chance boundaries.
    """
    g=obs._game;me=obs.me;ps=g.state.player_state
    k='P'+str(g.state.color_to_index[me]);enemy=next(c for c in g.state.colors if c!=me)
    ek='P'+str(g.state.color_to_index[enemy]);gap=g.vps_to_win-obs.my_actual_vps
    target=max(5,ps[ek+'_LONGEST_ROAD_LENGTH']+1) if ps[ek+'_HAS_ROAD'] else 5
    if (gap>2 or ps[k+'_HAS_ROAD'] or ps[k+'_ROADS_AVAILABLE']<2 or
        ps[k+'_LONGEST_ROAD_LENGTH']<target-2):return None,0,False
    if time.process_time()>=deadline:return None,0,True
    public=obs.opp_public_vps;count=obs.opp_dev_count;unseen=max(0,5-obs.my_devs['VICTORY_POINT'])
    h=hand(g.state,k);copies=roots=0
    types=(AT.MARITIME_TRADE,AT.PLAY_YEAR_OF_PLENTY,AT.PLAY_MONOPOLY,AT.PLAY_ROAD_BUILDING,AT.BUILD_ROAD)
    for root,a in enumerate(actions):
        if a.action_type not in types:continue
        if a.action_type==AT.BUILD_ROAD and (h[0]<2 or h[1]<2):continue
        if a.action_type==AT.MARITIME_TRADE:
            after=list(h)
            for r in a.value[:-1]:
                if r is not None:after[RES.index(r)]-=1
            after[RES.index(a.value[-1])]+=1
            if after[0]<2 or after[1]<2:continue
        if roots>=12 or copies>=80 or time.process_time()>=deadline:return None,copies,True
        first=g.copy();first.execute(a);copies+=1;roots+=1
        if public_terminal(first,me,public,count,unseen):return root,copies,False
        if first.state.current_color()!=me:continue
        if a.action_type!=AT.PLAY_ROAD_BUILDING and a.action_type!=AT.BUILD_ROAD:
            resources=hand(first.state,k)
            if resources[0]<2 or resources[1]<2:continue
        # A root road already pays for one of the two road actions.
        levels=1 if a.action_type==AT.BUILD_ROAD else 2
        frontier=[first]
        for level in range(levels):
            following=[]
            for state in frontier:
                for road in state.playable_actions:
                    if road.action_type!=AT.BUILD_ROAD:continue
                    if copies>=80 or time.process_time()>=deadline:return None,copies,True
                    child=state.copy();child.execute(road);copies+=1
                    if public_terminal(child,me,public,count,unseen):return root,copies,False
                    if child.state.current_color()==me:following.append(child)
            # Extend longest intermediate roads first, at most8 frontier states.
            frontier=sorted(following,key=lambda x:-x.state.player_state[k+'_LONGEST_ROAD_LENGTH'])[:8]
    return None,copies,False
