from public_context import Context, CITY
from catanatron.models.board import STATIC_GRAPH

class SpatialContext(Context):
    def __init__(self,game,me):
        super().__init__(game,me,True)
        self.geometry={}

    def spatial_plans(self, g):
        st, b, ps = g.state, g.state.board, g.state.player_state
        signature = (tuple(sorted(b.buildings.items())), tuple(sorted(b.roads.items())),
                     b.robber_coordinate, ps[self.key+'_CITIES_AVAILABLE'],
                     ps[self.key+'_SETTLEMENTS_AVAILABLE'], ps[self.key+'_ROADS_AVAILABLE'])
        if signature in self.geometry:
            return self.geometry[signature]
        blocked = self.by_tile.get(b.robber_coordinate, ())
        def gain(node):
            return max(0.0, sum(self.rates.get(node, ()))
                       - sum(p for n,_,p in blocked if n == node))
        plans = []
        cities = st.buildings_by_color[self.me]['SETTLEMENT']
        if cities and ps[self.key+'_CITIES_AVAILABLE'] > 0:
            plans.append(('city', CITY, 1, max(gain(n) for n in cities), 0))
        if ps[self.key+'_SETTLEMENTS_AVAILABLE'] > 0:
            frontier = set().union(*b.connected_components[self.me]) if b.connected_components[self.me] else set()
            seen = set(frontier)
            for depth in range(min(2, ps[self.key+'_ROADS_AVAILABLE']) + 1):
                sites = frontier.intersection(b.board_buildable_ids)
                if sites:
                    cost = (1+depth, 1+depth, 1, 1, 0)
                    plans.append(('expand', cost, 1, max(gain(n) for n in sites), 0))
                new = set()
                for n in sorted(frontier):
                    if b.is_enemy_node(n, self.me):
                        continue
                    for m in STATIC_GRAPH.neighbors(n):
                        if m in b.map.land_nodes and m not in seen and not b.is_enemy_road((n,m),self.me):
                            new.add(m)
                seen.update(new)
                frontier = new
        self.geometry[signature] = tuple(plans)
        return self.geometry[signature]
