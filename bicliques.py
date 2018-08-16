from os import remove
from subprocess import check_call
from tempfile import NamedTemporaryFile


class MaximalBicliques():
    """
    Python wrapper for C++ implementation of Maximal Biclique enumeration
    algorithm (http://citeseer.nj.nec.com/alexe02consensus.html). The C++
    code files and setup instructions for sbtest can be found at
    http://genome.cs.iastate.edu/supertree/download/biclique/.
    """

    def __init__(self, sbtestloc, store_temps=False):
        """ Specify the location of sbtest file while inititlizing
        the class. """

        self.sbtestloc = sbtestloc
        self.store_temps = store_temps

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

        # Create temporary files.
        temp_input = NamedTemporaryFile(delete=False)
        temp_output = NamedTemporaryFile(delete=False)
        temp_output_size = NamedTemporaryFile(delete=False)

        # Write the serialsed edges.
        with open(temp_input.name, 'w') as f:
            for e1, e2 in self._serialized_edges:
                f.write("%d\t%d\n" % (e1, e2))

        self._temp_input, self._temp_output, self._temp_output_size =\
            temp_input, temp_output, temp_output_size

    def _run_biclique_command(self):
        check_call(['./sbtest', self._temp_input.name, self._temp_output.name,
                    self._temp_output_size.name],
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
        with open(self._temp_output.name, 'r') as f:
            bic = f.read().split('\n\n')[:-1]
            for i, b in enumerate(bic):
                spl = b.split('\n')
                texta = [self._id2nodea[int(i)] for i in spl[0].split()]
                textb = [self._id2nodeb[int(i)] for i in spl[1].split()]
                bicliques.append([texta, textb])

        self.bicliques = bicliques
        self.num_bicliques = len(bicliques)

        if not self.store_temps:
            # Delete temporary files.
            remove(self._temp_input.name)
            remove(self._temp_output.name)
            remove(self._temp_output_size.name)
