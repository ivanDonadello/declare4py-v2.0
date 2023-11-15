import json
import re
from tqdm import tqdm
from Declare4Py.bpmnconstraints.utils.script_utils import Setup
from Declare4Py.bpmnconstraints.parser.bpmn_parser import Parser
from Declare4Py.bpmnconstraints.compiler.bpmn_compiler import Compiler
from Declare4Py.bpmnconstraints.utils.plot import Plot
from Declare4Py.bpmnconstraints.utils.constants import (
    DISCARDED_CONSTRAINTS,
    DECLARE_GATEWAYS,
    DECLARE_CONSTRAINT_REGEX_PATTERN,
)


class ComparisonScript:
    def __init__(self, dataset_path, dataframe_path, create_plots) -> None:
        self.dataset_path = dataset_path
        self.dataframe_path = dataframe_path
        self.setup = Setup(None)
        self.plot = Plot()
        self.transitivity = True
        self.create_plot = create_plots

    def __print_model(self, model):
        print(json.dumps(model, indent=2))

    def run(self):
        petri_net_models = self.__parse_dataframe()
        compiler_models = self.__parse_dataset()

        models = self.__combine_models(petri_net_models, compiler_models)

        recall = []
        precision = []

        for model in models:
            recall.append(model.get("recall"))
            precision.append(model.get("precision"))

        mean_recall = sum(recall) / len(recall)
        mean_precision = sum(precision) / len(precision)

        f1_score = 2 * ((mean_precision * mean_recall) / (mean_recall + mean_precision))

        print(f"Mean Precision: {mean_precision}")
        print(f"Mean Recall: {mean_recall}")
        print(f"F1 Score: {f1_score}")

        if self.create_plot:
            self.plot.scatter_plot_recall_precision_combined(models)
            self.plot.scatter_plot_precision_element_types(models)
            self.plot.scatter_plot_recall_element_types(models)
            self.plot.bar_plot_total_generated_constraints(models)

    def __parse_dataframe(self):
        df = self.setup.load_dataframe(self.dataframe_path)
        models = []

        for _, row in tqdm(df.iterrows(), "Parsing dataframe"):
            model = {
                "model id": row["model_id"],
                "constraints": [],
            }

            for constraint in row["constraints"]:
                constraint = constraint[: constraint.find("|")].strip()

                discarded_constraint = constraint
                if discarded_constraint.split("[")[0] in DISCARDED_CONSTRAINTS:
                    continue

                model["constraints"].append(constraint)
            models.append(model)
        return models

    def __parse_dataset(self):
        compiled_models = []

        for chunk in tqdm(
            self.setup.read_csv_chunk(self.dataset_path), desc="Parsing dataset"
        ):
            models = self.setup.load_models(chunk)
            model_id = chunk["Model ID"]

            for i, model in enumerate(models):
                compiled_model = {
                    "model id": model_id.iloc[i],
                    "constraints": [],
                }

                try:
                    parser = Parser(model, False, self.transitivity)

                    if parser.count_pools() > 1:
                        continue

                    result = parser.run()

                    if not parser.has_start():
                        continue
                    if parser.count_model_elements() < 5:
                        continue
                    if parser.contains_multiple_starts():
                        continue
                    if parser.or_multiple_paths():
                        continue

                    num_model_elements = parser.count_model_elements()
                    num_model_element_types = parser.count_model_element_types()
                    element_types = parser.get_element_types()

                    compiled_model.update(
                        {
                            "number of elements": num_model_elements,
                            "number of element types": num_model_element_types,
                            "element types": element_types,
                        }
                    )

                    compiler = Compiler(result, self.transitivity)
                    result = compiler.run()

                    for constraint in result:
                        compiled_model["constraints"].append(constraint.get("DECLARE"))

                    compiled_models.append(compiled_model)

                except Exception:
                    continue
        return compiled_models

    def __remove_init_constraints(self, model):
        petri_net_constraints = model.get("petri net constraints")
        compiler_constraints = model.get("compiler constraints")

        petri_net_constraints = [
            x for x in petri_net_constraints if not x.startswith("Init")
        ]
        compiler_constraints = [
            x for x in compiler_constraints if not x.startswith("Init")
        ]

        model["petri net constraints"] = petri_net_constraints
        model["compiler constraints"] = compiler_constraints

    def __remove_end_constraints(self, model):
        petri_net_constraints = model.get("petri net constraints")
        compiler_constraints = model.get("compiler constraints")

        petri_net_constraints = [
            x for x in petri_net_constraints if not x.startswith("End")
        ]
        compiler_constraints = [
            x for x in compiler_constraints if not x.startswith("End")
        ]

        model["petri net constraints"] = petri_net_constraints
        model["compiler constraints"] = compiler_constraints

    def __rearrange_gateway_order(
        self, petri_net_constraints, compiler_constraints, model_id
    ):
        for i, compiler_constraint in enumerate(compiler_constraints):
            if compiler_constraint.startswith(tuple(DECLARE_GATEWAYS)):
                match = re.match(DECLARE_CONSTRAINT_REGEX_PATTERN, compiler_constraint)
                if match:
                    arguments = match.group(2).split(", ")
                    compiler_constraint_set = set(
                        [match.group(1), arguments[0], arguments[1]]
                    )
                    for petri_net_constraint in petri_net_constraints:
                        if petri_net_constraint.startswith(tuple(DECLARE_GATEWAYS)):
                            match = re.match(
                                DECLARE_CONSTRAINT_REGEX_PATTERN, compiler_constraint
                            )
                            if match:
                                arguments = match.group(2).split(", ")
                                petri_net_constraint_set = set(
                                    [match.group(1), arguments[0], arguments[1]]
                                )
                                if compiler_constraint_set == petri_net_constraint_set:
                                    if sorted(compiler_constraint) == sorted(
                                        petri_net_constraint
                                    ):
                                        compiler_constraints[i] = petri_net_constraint

    def __gateway_constraints_exists(self, compiler_constraints):
        return any(
            constraint.startswith(tuple(DECLARE_GATEWAYS))
            for constraint in compiler_constraints
        )

    def __combine_models(self, petri_net_models, compiler_models):
        combined_models = []

        for petri_net_model in tqdm(petri_net_models, desc="Combining models"):
            model_id = petri_net_model.get("model id")
            petri_net_constraints = petri_net_model.get("constraints")
            found_matching_model = False

            for compiler_model in compiler_models:
                if compiler_model.get("model id") == model_id:
                    compiler_constraints = compiler_model.get("constraints")
                    number_of_elements = compiler_model.get("number of elements")
                    number_of_element_types = compiler_model.get(
                        "number of element types"
                    )
                    element_types = compiler_model.get("element types")
                    found_matching_model = True
                    break

            if (
                found_matching_model
                and len(compiler_constraints) > 0
                and len(petri_net_constraints) > 0
            ):
                if self.__gateway_constraints_exists(compiler_constraints):
                    self.__rearrange_gateway_order(
                        petri_net_constraints, compiler_constraints, model_id
                    )

                combined_models.append(
                    {
                        "model id": model_id,
                        "petri net constraints": list(set(petri_net_constraints)),
                        "compiler constraints": list(set(compiler_constraints)),
                        "number of elements": number_of_elements,
                        "number of element types": number_of_element_types,
                        "element types": element_types,
                        "precision": self.__calculate_precision(
                            petri_net_constraints, compiler_constraints
                        ),
                        "recall": self.__calculate_recall(
                            petri_net_constraints, compiler_constraints
                        ),
                    }
                )

        return combined_models

    def __calculate_precision(self, petri_net_constraints, compiler_constraints):
        return len(
            set(petri_net_constraints).intersection(set(compiler_constraints))
        ) / len(set(compiler_constraints))

    def __calculate_recall(self, petri_net_constraints, compiler_constraints):
        return len(
            set(compiler_constraints).intersection(set(petri_net_constraints))
        ) / len(set(petri_net_constraints))
