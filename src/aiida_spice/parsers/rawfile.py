from aiida.common.exceptions import OutputParsingError
from aiida.orm import ArrayData, Dict
from aiida.parsers.parser import Parser
from spicelib import RawRead


class RawfileParser(Parser):
    """
    AiiDA Parser subclass for parsing Berkeley SPICE3 rawfile outputs using `spicelib`.
    """

    def parse(self, **kwargs):
        """
        Parses retrieved SPICE3 rawfiles.

        :returns: An exit code indicating success or specific failure modes.
        """
        # Check that the retrieved folder exists
        try:
            retrieved = self.retrieved
        except OutputParsingError:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER
        output_filename = self.node.get_option("output_filename")

        # Check if output raw file exists in the retrieved files
        if output_filename not in retrieved.list_object_names():
            return self.exit_codes.ERROR_MISSING_OUTPUT_FILE

        # Write retrieved stream to a temporary file (spicelib requires a file path)
        with retrieved.open(output_filename, "rb") as handle:
            # Load raw data via spicelib
            raw_data = RawRead(handle)

            # Store trace arrays (sanitize variable names for AiiDA array keys)
            array_node = ArrayData()
            trace_names = raw_data.get_trace_names()
            for trace in trace_names:
                wave_data = raw_data.get_trace(trace).get_wave()

                # Convert SPICE variable syntax e.g. v(1) -> v_1 to conform to standard array naming
                sanitized_key = trace.replace("(", "_").replace(")", "").replace("/", "_div_")
                array_node.set_array(sanitized_key, wave_data)

            # Store simulation metadata in Dict node
            metadata = {
                "title": getattr(raw_data, "title", "Unknown"),
                "date": getattr(raw_data, "date", "Unknown"),
                "plot_name": getattr(raw_data, "plot_name", "Unknown"),
                "flags": getattr(raw_data, "flags", []),
                "number_of_variables": raw_data.nVariables,
                "number_of_points": raw_data.nPoints,
                "variables": trace_names,
            }
            dict_node = Dict(dict=metadata)

        # Attach output nodes to the parser outputs
        self.out("output_parameters", dict_node)
        self.out("output_arrays", array_node)

        return self.exit_codes.OK
