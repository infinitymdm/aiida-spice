import re
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

        # Check if output files are present in the retrieved files
        rawfile_name = self.node.get_option("rawfile_name")
        if rawfile_name not in retrieved.list_object_names():
            return self.exit_codes.ERROR_MISSING_RAWFILE
        stdout_name = self.node.get_option("stdout_name")
        if stdout_name not in retrieved.list_object_names():
            return self.exit_codes.ERROR_MISSING_STDOUT

        # Extract outputs to a temporary file for parsing with spicelib
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_filepath = Path(tmpdir) / rawfile_name
            with retrieved.open(rawfile_name, "rb") as source, open(tmp_filepath, "wb") as target:
                target.write(source.read())

            # Load raw data via spicelib
            try:
                raw_data = RawRead(tmp_filepath, dialect=self.node.get_option("parser_dialect"))
            except SpiceReadException as e:
                self.logger.error(f"Failed to parse the SPICE3 rawfile: {e}")
                return self.exit_codes.ERROR_PARSING_RAWFILE

            # Store trace arrays, sanitizing variable names for keys
            wave_node = ArrayData()
            for trace in raw_data.get_trace_names():
                sanitized_key = sanitize(trace)
                wave_node.set_array(sanitized_key, raw_data.get_trace(trace).get_wave())

            # Store simulation metadata in Dict node
            properties = {str(k).replace(".", ""): v for k, v in raw_data.get_raw_properties().items()}
            properties.pop("Filename", None)
            properties.pop("Variables", None)
            metadata_node = Dict(dict=properties)

        # Read measurement results from stdout
        with retrieved.open(stdout_name, "r") as handle:
            measure_node = Dict()
            in_measure_block = False
            for line in handle.readlines():
                if line.isspace() or line.strip("-").isspace():
                    continue
                if line.strip().startswith("Measurement"):
                    in_measure_block = True
                elif in_measure_block and "=" in line:
                    [k, v, *_] = re.split(r"[=\s]+", line)
                    measure_node[k] = float(v)
                else:
                    in_measure_block = False

        # Attach output nodes to the parser outputs
        self.out("metadata", metadata_node)
        self.out("measurements", measure_node)
        self.out("trace_data", wave_node)
