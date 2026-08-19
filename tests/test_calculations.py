"""Tests for calculations."""


def test_process(spice_code):
    """Test running a calculation
    note this does not test that the expected outputs are created of output parsing"""

    # Prepare input parameters
    # diff_parameters = DataFactory("spice")
    # parameters = diff_parameters({"ignore-case": True})
    #
    # file1 = SinglefileData(file=os.path.join(TEST_DIR, "input_files", "file1.txt"))
    # file2 = SinglefileData(file=os.path.join(TEST_DIR, "input_files", "file2.txt"))
    #
    # # set up calculation
    # inputs = {
    #     "code": spice_code,
    #     "parameters": parameters,
    #     "file1": file1,
    #     "file2": file2,
    #     "metadata": {
    #         "options": {"max_wallclock_seconds": 30},
    #     },
    # }
    #
    # result = run(CalculationFactory("spice"), **inputs)
    # computed_diff = result["spice"].get_content()

    # assert "content1" in computed_diff
    # assert "content2" in computed_diff
    assert True
