import matplotlib.pyplot as plt
import networkx as nx
from utils import *
from heapq import heappop, heappush
from itertools import count
from networkx.algorithms.shortest_paths.weighted import _weight_function

from queue import PriorityQueue

G = nx.DiGraph()
TRAFFIC_JAM_FACTOR = 5 # Multiplicidade do impacto do trânsito na rota

class Graph():
    def __init__(self):
        edges = readInput()

        for edge in edges:
            G.add_edge(edge[0], edge[1], weight=edge[2], intensity=edge[3])
        
        self.pos = nx.spring_layout(G)

    def getNodes(self):
        return G.nodes()

    def drawEdgeList(self, edgeList, color, style, curved):
        if (curved):
            nx.draw_networkx_edges(
                G,
                self.pos,
                edgelist=edgeList,
                width=1,
                edge_color=color,
                style=style,
                arrows=True,
                arrowstyle="-|>",
                arrowsize=10,
                connectionstyle='arc3, rad = 0.25'
            )
            return

        nx.draw_networkx_edges(
            G,
            self.pos,
            edgelist=edgeList,
            width=1,
            edge_color=color,
            style=style,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=10
        )

    def drawGraph(self):
        # nodes
        nx.draw_networkx_nodes(G, self.pos, node_size=400)

        # edges
        curvedEdges = [edge for edge in G.edges() if reversed(edge) in G.edges()]
        straightEdges = list(set(G.edges()) - set(curvedEdges))
        trafficCurvedEdges = [edge for edge in curvedEdges if G.edges[edge]['intensity'] != 0]
        trafficStraightEdges = [edge for edge in straightEdges if G.edges[edge]['intensity'] != 0]
        curvedEdges = list(set(curvedEdges) - set(trafficCurvedEdges))
        straightEdges = list(set(straightEdges) - set(trafficStraightEdges))

        self.drawEdgeList(curvedEdges, "k", "solid", True)
        self.drawEdgeList(straightEdges, "k", "solid", False)
        self.drawEdgeList(trafficCurvedEdges, "k", "dashed", True)
        self.drawEdgeList(trafficStraightEdges, "k", "dashed", False)

        nx.draw_networkx_labels(G, self.pos, font_size=12, font_family="sans-serif") # node labels
        edge_labels = nx.get_edge_attributes(G, "weight") # edge weight labels
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels, font_color="orange")

        ax = plt.gca()
        ax.margins(0.08)
        plt.axis("off")
        plt.tight_layout()
        plt.show()

        plt.savefig("network.png")

    def drawPath(self, path):
        pathEdges = []
        for i in range(len(path) - 1):
            pathEdges.append((path[i], path[i+1]))

        # edges
        curvedEdges = [edge for edge in G.edges() if reversed(edge) in G.edges()]
        curvedPathEdges = [edge for edge in pathEdges if edge in curvedEdges]
        pathEdges = list(set(pathEdges) - set(curvedPathEdges))

        self.drawEdgeList(curvedPathEdges, "r", "solid", True)
        self.drawEdgeList(pathEdges, "r", "solid", False)

        # edge weight labels
        edge_labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels, font_color="orange")

        plt.savefig("network-path.png")
    
    def getShortestPath(self, source, target):
        'Return the shortest path from source to target using Dijkstra algorithm'
        return nx.shortest_path(G, source, target, weight='weight')

    def getSimplestPath(self, source, target):
        'Return the simplest path from source to target using BFS algorithm'
        return nx.shortest_path(G, source, target, weight=None)

    # def astar_path(self, source, target, weight="weight"):
    #     if source not in G or target not in G:
    #         msg = f"Either source {source} or target {target} is not in G"
    #         raise nx.NodeNotFound(msg)

    #     push = heappush
    #     pop = heappop
    #     weight = _weight_function(G, weight)

    #     # The queue stores priority, node, cost to reach, and parent.
    #     # Uses Python heapq to keep in priority order.
    #     # Add a counter to the queue to prevent the underlying heap from
    #     # attempting to compare the nodes themselves. The hash breaks ties in the
    #     # priority and is guaranteed unique for all nodes in the graph.
    #     c = count()
    #     queue = [(0, next(c), source, 0, None)]

    #     # Maps enqueued nodes to distance of discovered paths and the
    #     # computed heuristics to target. We avoid computing the heuristics
    #     # more than once and inserting the node into the queue too many times.
    #     enqueued = {}
    #     # Maps explored nodes to parent closest to the source.
    #     explored = {}

    #     while queue:
    #         # Pop the smallest item from queue.
    #         _, __, curnode, dist, parent = pop(queue)

    #         if curnode == target:
    #             path = [curnode]
    #             node = parent
    #             while node is not None:
    #                 path.append(node)
    #                 node = explored[node]
    #             path.reverse()
    #             return path

    #         if curnode in explored:
    #             # Do not override the parent of starting node
    #             if explored[curnode] is None:
    #                 continue

    #             # Skip bad paths that were enqueued before finding a better one
    #             qcost, h = enqueued[curnode]
    #             if qcost < dist:
    #                 continue

    #         explored[curnode] = parent
    #         for neighbor, w in G[curnode].items():
    #             ncost = dist + weight(curnode, neighbor, w)
    #             if neighbor in enqueued:
    #                 qcost, h = enqueued[neighbor]
    #                 # print(neighbor, enqueued[neighbor])
    #                 # print(curnode, neighbor, qcost, ncost, h)

    #                 # if qcost <= ncost, a less costly path from the
    #                 # neighbor to the source was already determined.
    #                 # Therefore, we won't attempt to push this neighbor
    #                 # to the queue
    #                 if qcost <= ncost:
    #                     continue

    #             else:
    #                 h = TRAFFIC_JAM_FACTOR * G.get_edge_data(curnode, neighbor)['intensity']

    #             enqueued[neighbor] = ncost, h
    #             print(neighbor, enqueued[neighbor])
    #             push(queue, (ncost + h, next(c), neighbor, ncost, curnode))

    #     raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")

    def aStar(self, source, target):
        if source not in G or target not in G:
            msg = f"Either source {source} or target {target} is not in G"
            raise nx.NodeNotFound(msg)
        
        OPEN = PriorityQueue()
        CLOSED = {}

        OPEN.put((0, source, 0, None))

        while not OPEN.empty():
            _, curnode, dist, parent = OPEN.get()

            if curnode == target:
                path = [curnode]
                node = parent
                while node is not None:
                    path.append(node)
                    print(CLOSED[node])
                    node = CLOSED[node][1]
                path.reverse()
                return path

            CLOSED[curnode] = (dist, parent)

            for neighbor, w in G[curnode].items():
                cost = dist + G.get_edge_data(curnode, neighbor)['weight']

                if neighbor in CLOSED:
                    if CLOSED[neighbor][0] <= cost:
                        continue
                    else:
                        CLOSED.pop(neighbor)

                if neighbor not in OPEN.queue and neighbor not in CLOSED:
                    h = TRAFFIC_JAM_FACTOR * G.get_edge_data(curnode, neighbor)['intensity']
                    OPEN.put((cost + h, neighbor, cost + h, curnode))
                    CLOSED[neighbor] = (cost + h, curnode)

        raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")

