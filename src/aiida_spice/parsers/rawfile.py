from aiida.common.exceptions import OutputParsingError
from aiida.orm import ArrayData, Dict
from aiida.parsers.parser import Parser
from spicelib import RawRead, SpiceReadException


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

        # Load raw data via spicelib
        try:
            raw_data = RawRead(output_filename)
        except SpiceReadException as e:
            self.logger.error(f"Failed to parse SPICE3 rawfile: {e}")
            return self.exit_codes.ERROR_PARSING_FILE

        # Store trace arrays, sanitizing variable names for keys
        array_node = ArrayData()
        for trace in raw_data.get_trace_names():
            # Convert SPICE variable syntax e.g. v(1) -> v_1 to conform to standard array naming
            sanitized_key = trace.replace("(", "_").replace(")", "").replace("/", "__")
            array_node.set_array(sanitized_key, raw_data.get_trace(trace).get_wave())

        # Store simulation metadata in Dict node
        dict_node = Dict(dict=raw_data.get_raw_properties())

        # Attach output nodes to the parser outputs
        self.out("output_parameters", dict_node)
        self.out("output_arrays", array_node)

        return self.exit_codes.OK
