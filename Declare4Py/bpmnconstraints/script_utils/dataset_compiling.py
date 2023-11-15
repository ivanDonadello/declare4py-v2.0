from json import dumps
from tqdm import tqdm
from numpy import median, average
from Declare4Py.bpmnconstraints.parser.bpmn_parser import Parser
from Declare4Py.bpmnconstraints.compiler.bpmn_compiler import Compiler
from Declare4Py.bpmnconstraints.utils.script_utils import Setup


class CompilingScript:
    def __init__(self, path, transitivity, print_models) -> None:
        self.setup = Setup(path)
        self.transitivity = transitivity
        self.print_models = print_models
        self.total_constraints = 0
        self.total_unique_constraints = 0
        self.constraints_len = []

    def run(self):
        for filename in tqdm(self.setup.get_files()):
            csv_file = self.setup.get_file(filename)

            if self.setup.is_file(csv_file):
                for chunk in self.setup.read_csv_chunk(csv_file):
                    models = self.setup.load_models(chunk)

                    for model in models:
                        try:
                            parser = Parser(model, False, self.transitivity)

                            if parser.count_pools() > 1:
                                continue

                            result = parser.run()

                            if not parser.has_start():
                                continue

                            if parser.count_model_elements() < 5:
                                continue

                            result = Compiler(result, self.transitivity).run()
                            self.total_constraints += len(result)
                            self.constraints_len.append(len(result))

                            if self.print_models:
                                print(dumps(result, indent=2))

                        except Exception:
                            pass
        print(f"Total generated constraints: {self.total_constraints}")
        print(f"Median: {round(median(self.constraints_len))}")
        print(f"Average: {round(average(self.constraints_len))}")
