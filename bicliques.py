from os import remove, path
from subprocess import check_call
from tempfile import NamedTemporaryFile


class MaximalBicliques():
    """
    Python wrapper for C++ implementation of Maximal Biclique enumeration
    algorithm (http://citeseer.nj.nec.com/alexe02consensus.html). The C++
    code files and setup instructions for sbtest can be found at
    http://genome.cs.iastate.edu/supertree/download/biclique/.
    """

    def __init__(self, sbtestloc='max-biclique',
                 input_addr=None, output_addr=None, output_size_addr=None,
                 store_temps=False):
        """ Specify the location of sbtest file while inititlizing
        the class. """

        self.sbtestloc = path.join(path.dirname(__file__), sbtestloc)
        self.store_temps = store_temps

        # Create temporary files.
        self._input_addr = path.abspath(input_addr)\
            if input_addr else NamedTemporaryFile(delete=False).name
        self._output_addr = path.abspath(output_addr)\
            if output_addr else NamedTemporaryFile(delete=False).name
        self._output_size_addr = path.abspath(output_size_addr)\
            if output_size_addr else NamedTemporaryFile(delete=False).name

    def _serialize_edges(self):
        """ Gives a unique ID to each node and stores the mappings. """

        # Convert edge labels to id.
        nodes_a = set([e[0] for e in self.edge_list])
        nodes_b = set([e[1] for e in self.edge_list])
        self.num_unique_nodes = tuple([len(nodes_a), len(nodes_b)])
        self._nodea2id = {text: i for i, text in enumerate(list(nodes_a))}
        self._nodeb2id = {text: i for i, text in enumerate(list(nodes_b))}

        # Store reverse mapping for later use.
        self._id2nodea = {i: text for text, i in self._nodea2id.items()}
        self._id2nodeb = {i: text for text, i in self._nodeb2id.items()}

        # Convert nodes in edge to list to their respective ids.
        self._serialized_edges = \
            [[self._nodea2id[e[0]], self._nodeb2id[e[1]]]
             for e in self.edge_list]

    def _write_temp_files(self):
        """ Writes the serialised edge lists to temporary files on disk. """

        # Write the serialsed edges.
        with open(self._input_addr, 'w') as f:
            for e1, e2 in self._serialized_edges:
                f.write("%d\t%d\n" % (e1, e2))

    def _run_biclique_command(self):
        check_call(['./sbtest', self._input_addr, self._output_addr,
                    self._output_size_addr],
                   cwd=self.sbtestloc)

    def calculate_bicliques(self, edge_list):
        """ Calculates the maximal bicliques from the supplied edge
        list. The edge list should be a list of lists. """

        assert (type(edge_list) == list) and (type(edge_list[0]) == list), (
            "Please input the edge list as a list of lists."
        )

        self.edge_list = edge_list
        self.num_edges = len(edge_list)
        self._serialize_edges()
        self._write_temp_files()
        self._run_biclique_command()

        bicliques = list()
        with open(self._output_addr, 'r') as f:
            for bic in f.read().split('\n\n')[:-1]:
                spl = bic.split('\n')
                texta = [self._id2nodea[int(i)] for i in spl[0].split()]
                textb = [self._id2nodeb[int(i)] for i in spl[1].split()]
                bicliques.append([texta, textb])

        self.bicliques = bicliques
        self.num_bicliques = len(bicliques)

        if not self.store_temps:
            # Delete temporary files.
            remove(self._input_addr)
            remove(self._output_addr)
            remove(self._output_size_addr)
