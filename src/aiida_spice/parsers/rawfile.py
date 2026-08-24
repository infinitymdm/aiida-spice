import tempfile
from pathlib import Path

from aiida.common.exceptions import OutputParsingError
from aiida.orm import ArrayData, Dict
from aiida.parsers.parser import Parser
from aiida_spice.utils.sanitize_variables import sanitize
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

        # Check if output raw file exists in the retrieved files
        output_filename = self.node.get_option("output_filename")
        if output_filename not in retrieved.list_object_names():
            return self.exit_codes.ERROR_MISSING_RAWFILE_NAME

        # Extract outputs to a temporary file for parsing with spicelib
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_filepath = Path(tmpdir) / output_filename
            with retrieved.open(output_filename, "rb") as source, open(tmp_filepath, "wb") as target:
                target.write(source.read())

            # Load raw data via spicelib
            try:
                raw_data = RawRead(tmp_filepath, dialect=self.node.get_option("parser_dialect"))
            except SpiceReadException as e:
                self.logger.error(f"Failed to parse the SPICE3 rawfile: {e}")
                return self.exit_codes.ERROR_PARSING_RAWFILE

            # Store trace arrays, sanitizing variable names for keys
            array_node = ArrayData()
            for trace in raw_data.get_trace_names():
                array_node.set_array(sanitize(trace), raw_data.get_trace(trace).get_wave())

            # Store simulation metadata in Dict node
            properties = {str(k).replace(".", ""): v for k, v in raw_data.get_raw_properties().items()}
            properties.pop("Filename", None)
            properties_node = Dict(dict=properties)

        # Attach output nodes to the parser outputs
        self.out("output_parameters", properties_node)
        self.out("output_arrays", array_node)
