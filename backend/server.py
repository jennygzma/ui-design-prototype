# This file acts as a controller to route API requests

import datetime
import json
import uuid

import globals
from code_generation import get_fake_data as get_generated_fake_data
from code_generation import (
    get_iterate_code,
    implement_plan_lock_step,
    test_code_per_lock_step,
    wipeout_code,
)
from flask import Flask, jsonify, request
from planning import get_design_hypothesis as get_generated_design_hypothesis
from planning import get_plan as get_generated_plan
from planning import get_theories as get_generated_theories
from utils import create_and_write_file, create_folder, folder_exists, read_file

# Initializing flask app
app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


@app.route("/get_user_input", methods=["GET"])
def get_user_input():
    print("calling get_user_input...")
    print(globals.prompt)
    return jsonify({"message": "getting user input", "user_input": globals.prompt}), 200


@app.route("/generate_fake_data", methods=["POST"])
def generate_fake_data():
    print("calling generate_fake_data...")
    globals.prompt = request.json["prompt"]
    data = get_generated_fake_data(globals.prompt)
    globals.faked_data = data
    return jsonify({"message": "Generated data"}), 200


@app.route("/save_faked_data", methods=["POST"])
def save_faked_data():
    print("calling save_faked_data...")
    data = request.json
    globals.faked_data = data["faked_data"]
    create_and_write_file(
        f"{globals.folder_path}/{globals.FAKED_DATA_FILE_NAME}", globals.faked_data
    )
    return jsonify({"message": "Saved faked data"}), 200


@app.route("/get_faked_data", methods=["GET"])
def get_faked_data():
    print("calling get_faked_data...")
    return (
        jsonify({"message": "getting faked data", "faked_data": globals.faked_data}),
        200,
    )


@app.route("/brainstorm_theories", methods=["POST"])
def brainstorm_theories():
    print("calling brainstorm_theories...")
    globals.prompt = request.json["prompt"]
    date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if globals.folder_path is None:
        globals.folder_path = (
            f"{globals.GENERATED_FOLDER_PATH}/generations_{date_time}_{uuid.uuid4()}"
        )
        create_folder(globals.folder_path)
    create_and_write_file(
        f"{globals.folder_path}/{globals.USER_INPUT_FILE_NAME}", globals.prompt
    )
    new_theories = get_generated_theories(globals.prompt, globals.theories)
    globals.theories.extend(new_theories)
    create_and_write_file(
        f"{globals.folder_path}/{globals.THEORIES_FILE_NAME}",
        json.dumps(globals.theories),
    )
    return jsonify({"message": "Generated theories"}), 200


@app.route("/save_theory", methods=["POST"])
def save_theory():
    print("calling save_theories...")
    data = request.json
    globals.theories.append(data["theory"])
    create_and_write_file(
        f"{globals.folder_path}/{globals.THEORIES_FILE_NAME}",
        json.dumps(globals.theories),
    )
    return jsonify({"message": "Saved theory"}), 200


@app.route("/get_theories", methods=["GET"])
def get_theories():
    print("calling get_theories...")
    return jsonify({"message": "getting theories", "theories": globals.theories}), 200


@app.route("/save_selected_theories", methods=["POST"])
def save_selected_theories():
    print("calling save_selected_theories...")
    data = request.json
    globals.selected_theories = data["selected_theories"]
    create_and_write_file(
        f"{globals.folder_path}/{globals.SELECTED_THEORIES_FILE_NAME}",
        json.dumps(globals.selected_theories),
    )
    return jsonify({"message": "Saved selected theories"}), 200


@app.route("/get_selected_theories", methods=["GET"])
def get_selected_theories():
    print("calling get_selected_theories...")
    return (
        jsonify(
            {
                "message": "getting selected theories",
                "selected_theories": globals.selected_theories,
            }
        ),
        200,
    )


@app.route("/generate_design_hypothesis", methods=["POST"])
def generate_design_hypothesis():
    print("calling generate_design_hypothesis...")
    data = request.json
    globals.prompt = data["prompt"]
    globals.design_hypothesis = get_generated_design_hypothesis(
        globals.prompt, globals.faked_data
    )
    if folder_exists(f"{globals.folder_path}/1"):
        wipeout_code(globals.folder_path, 1, globals.plan)
    create_and_write_file(
        f"{globals.folder_path}/{globals.DESIGN_HYPOTHESIS_FILE_NAME}",
        globals.design_hypothesis,
    )
    create_and_write_file(
        f"{globals.folder_path}/{globals.FAKED_DATA_FILE_NAME}", globals.faked_data
    )
    globals.plan = []
    return (
        jsonify(
            {
                "message": "Generated design hypothesis",
                "hypothesis": globals.design_hypothesis,
            }
        ),
        200,
    )


@app.route("/save_design_hypothesis", methods=["POST"])
def save_design_hypothesis():
    print("calling save_design_hypothesis...")
    data = request.json
    globals.design_hypothesis = data["design_hypothesis"]
    if folder_exists(f"{globals.folder_path}/1"):
        wipeout_code(globals.folder_path, 1, globals.plan)
    create_and_write_file(
        f"{globals.folder_path}/{globals.DESIGN_HYPOTHESIS_FILE_NAME}",
        globals.design_hypothesis,
    )
    globals.plan = []
    return (
        jsonify(
            {"message": "Saved design hypothesis", "data": globals.design_hypothesis}
        ),
        200,
    )


@app.route("/get_design_hypothesis", methods=["GET"])
def get_design_hypothesis():
    print("calling get_design_hypothesis...")
    return (
        jsonify(
            {
                "message": "getting design hypothesis",
                "design_hypothesis": globals.design_hypothesis,
            }
        ),
        200,
    )


@app.route("/generate_plan", methods=["POST"])
def generate_plan():
    print("calling generate_plan...")
    plan = get_generated_plan(globals.design_hypothesis)
    print(plan)
    globals.plan = plan
    if folder_exists(f"{globals.folder_path}/1"):
        wipeout_code(globals.folder_path, 1, globals.plan)
    create_and_write_file(
        f"{globals.folder_path}/{globals.PLAN_FILE_NAME}", json.dumps(globals.plan)
    )
    globals.task_map = {
        int(task["task_id"]): {
            "task": task["task"],
            globals.CURRENT_DEBUG_ITERATION: 0,
            globals.DEBUG_ITERATION_MAP: {},
        }
        for task in plan
    }
    create_and_write_file(
        f"{globals.folder_path}/{globals.TASK_MAP_FILE_NAME}",
        json.dumps(globals.task_map),
    )
    print(globals.task_map)
    return jsonify({"message": "Generated Plan", "plan": plan}), 200


@app.route("/get_plan", methods=["GET"])
def get_plan():
    print("calling get_plan...")
    print("task_map", globals.task_map)
    task_list = [
        {
            "task_id": task_id,
            "task": task_info["task"],
        }
        for task_id, task_info in sorted(globals.task_map.items())
    ]
    return jsonify({"message": "getting plan", "plan": json.dumps(task_list)}), 200


@app.route("/update_step_in_plan", methods=["POST"])
def update_step_in_plan():
    print("calling update_step_in_plan")
    data = request.json
    task_id = int(data["task_id"])
    new_task_description = data["task_description"]
    index = task_id - 1
    globals.plan[index]["task"] = new_task_description
    globals.task_map[task_id]["task"] = new_task_description
    if folder_exists(f"{globals.folder_path}/{task_id}"):
        wipeout_code(globals.folder_path, task_id, globals.plan)
    create_and_write_file(
        f"{globals.folder_path}/{globals.PLAN_FILE_NAME}", json.dumps(globals.plan)
    )
    create_and_write_file(
        f"{globals.folder_path}/{globals.TASK_MAP_FILE_NAME}",
        json.dumps(globals.task_map),
    )
    return (
        jsonify(
            {"message": f"Updated step in plan for {task_id}", "data": globals.plan}
        ),
        200,
    )


@app.route("/add_step_in_plan", methods=["POST"])
def add_step_in_plan():
    print("calling add_step_in_plan")
    data = request.json
    curr_task_id = int(data["current_task_id"])
    new_task_id = curr_task_id + 1
    new_task_description = data["new_task_description"]
    injected_index = new_task_id - 1
    new_task = {"task_id": None, "task": new_task_description, "dep": []}
    globals.plan.insert(injected_index, new_task)
    for i in range(injected_index, len(globals.plan)):
        globals.plan[i]["task_id"] = i + 1

    keys_to_shift = sorted(
        [key for key in globals.task_map if key >= new_task_id], reverse=True
    )
    for key in keys_to_shift:
        globals.task_map[key + 1] = globals.task_map.pop(key)
    globals.task_map[new_task_id] = {
        "task": new_task_description,
        globals.CURRENT_DEBUG_ITERATION: 0,
        globals.DEBUG_ITERATION_MAP: {},
    }
    globals.task_map = {key: globals.task_map[key] for key in sorted(globals.task_map)}

    if folder_exists(f"{globals.folder_path}/{new_task_id}"):
        wipeout_code(globals.folder_path, new_task_id, globals.plan)
    create_and_write_file(
        f"{globals.folder_path}/{globals.PLAN_FILE_NAME}", json.dumps(globals.plan)
    )
    create_and_write_file(
        f"{globals.folder_path}/{globals.TASK_MAP_FILE_NAME}",
        json.dumps(globals.task_map),
    )
    return (
        jsonify(
            {"message": f"Added step in plan for {new_task_id}", "data": globals.plan}
        ),
        200,
    )


@app.route("/remove_step_in_plan", methods=["POST"])
def remove_step_in_plan():
    print("calling remove_step_in_plan")
    data = request.json
    task_id = int(data["task_id"])
    index = task_id - 1
    globals.plan.pop(index)
    for i in range(index, len(globals.plan)):
        globals.plan[i]["task_id"] = i + 1

    globals.task_map.pop(task_id)
    keys_to_shift = sorted([key for key in globals.task_map if key > task_id])
    for key in keys_to_shift:
        globals.task_map[key - 1] = globals.task_map.pop(key)
    if folder_exists(f"{globals.folder_path}/{task_id}"):
        wipeout_code(globals.folder_path, task_id, globals.plan)
    create_and_write_file(
        f"{globals.folder_path}/{globals.PLAN_FILE_NAME}", json.dumps(globals.plan)
    )
    create_and_write_file(
        f"{globals.folder_path}/{globals.TASK_MAP_FILE_NAME}",
        json.dumps(globals.task_map),
    )
    return (
        jsonify(
            {"message": f"Removed step in plan for {task_id}", "data": globals.plan}
        ),
        200,
    )


# For testing only. Run curl http://127.0.0.1:5000/generate_code
@app.route("/generate_code", methods=["POST"])
def generate_code():
    print("calling generate_code...")
    data = request.json
    task_id = int(data["task_id"])
    task_code_folder_path = f"{globals.folder_path}/{task_id}"
    if folder_exists(task_code_folder_path):
        wipeout_code(globals.folder_path, task_id, globals.plan)
    implement_plan_lock_step(
        globals.design_hypothesis, globals.plan, globals.folder_path, task_id
    )
    task_main_code_folder_path = (
        f"{globals.folder_path}/{task_id}/{globals.MAIN_CODE_FILE_NAME}"
    )
    # file_path = implement_plan(globals.prompt, globals.plan, globals.faked_data, globals.design_hypothesis, globals.folder_path)
    code = read_file(task_main_code_folder_path)
    return jsonify({"message": "Generated code", "code": code}), 200


@app.route("/get_code_per_step", methods=["GET"])
def get_code_per_step():
    print("calling get_code_per_step...")
    task_id = request.args.get("task_id")
    task_main_code_folder_path = (
        f"{globals.folder_path}/{task_id}/{globals.MAIN_CODE_FILE_NAME}"
    )
    code = read_file(task_main_code_folder_path) or ""
    return jsonify({"message": f"grabbed code for {task_id}", "code": code}), 200


@app.route("/get_iteration_map_per_step", methods=["GET"])
def get_iteration_map_per_step():
    print("calling get_iteration_map_per_step...")
    task_id = int(request.args.get("task_id"))
    print(globals.task_map[task_id][globals.DEBUG_ITERATION_MAP])
    return (
        jsonify(
            {
                "message": f"grabbed iteration_map for {task_id}",
                "iterations": globals.task_map[task_id][globals.DEBUG_ITERATION_MAP],
            }
        ),
        200,
    )


@app.route("/get_code_per_step_per_iteration", methods=["GET"])
def get_code_per_step_per_iteration():
    print("calling get_code_per_step_per_iteration...")
    task_id = request.args.get("task_id")
    iteration = request.args.get("iteration")
    code_folder_path = ""
    if iteration == "0":
        code_folder_path = (
            f"{globals.folder_path}/{task_id}/{globals.CLEANED_CODE_FILE_NAME}"
        )
    else:
        code_folder_path = f"{globals.folder_path}/{task_id}/{globals.ITERATION_FOLDER_NAME}/{iteration}/{globals.ITERATION_CLEANED_FILE_NAME}"
    code = read_file(code_folder_path) or ""
    create_and_write_file(
        f"{globals.folder_path}/{task_id}/{globals.MAIN_CODE_FILE_NAME}", code
    )
    return (
        jsonify(
            {
                "message": f"grabbed code for {task_id} and iteration {iteration}",
                "code": code,
            }
        ),
        200,
    )


@app.route("/delete_code_per_step_per_iteration", methods=["POST"])
def delete_code_per_step_per_iteration():
    print("calling delete_code_per_step_per_iteration...")
    task_id = int(request.args.get("task_id"))
    iteration = request.args.get("iteration")
    print(
        f"before, task id {task_id} iteration {iteration}, {globals.task_map[task_id][globals.DEBUG_ITERATION_MAP]}"
    )
    globals.task_map[task_id][globals.DEBUG_ITERATION_MAP].pop(iteration, None)
    print(
        f"after, task id {task_id} iteration {iteration}, {globals.task_map[task_id][globals.DEBUG_ITERATION_MAP]}"
    )
    create_and_write_file(
        f"{globals.folder_path}/{globals.TASK_MAP_FILE_NAME}",
        json.dumps(globals.task_map),
    )
    return jsonify({"message": f"deleted iteration for {task_id} {iteration}"}), 200


@app.route("/save_code_per_step", methods=["POST"])
def save_code_per_step():
    print("calling get_code_per_step...")
    data = request.json
    task_id = data["task_id"]
    code = data["code"]
    task_main_code_folder_path = (
        f"{globals.folder_path}/{task_id}/{globals.MAIN_CODE_FILE_NAME}"
    )
    create_and_write_file(task_main_code_folder_path, code)
    print(code)
    return jsonify({"message": f"Grabbed code for {task_id}", "code": code}), 200


@app.route("/iterate_code", methods=["POST"])
def iterate_code():
    print("calling iterate_code...")
    data = request.json
    task_id = data["task_id"]
    problem = data["problem"]
    globals.task_map[task_id][globals.CURRENT_DEBUG_ITERATION] = (
        globals.task_map[task_id][globals.CURRENT_DEBUG_ITERATION] + 1
    )
    current_debug_iteration = globals.task_map[task_id][globals.CURRENT_DEBUG_ITERATION]
    globals.task_map[task_id][globals.DEBUG_ITERATION_MAP][
        str(current_debug_iteration)
    ] = problem
    print(globals.task_map)
    create_and_write_file(
        f"{globals.folder_path}/{globals.TASK_MAP_FILE_NAME}",
        json.dumps(globals.task_map),
    )
    task = globals.task_map[task_id]["task"]
    task_code_folder_path = f"{globals.folder_path}/{task_id}"
    current_iteration_folder_path = f"{task_code_folder_path}/{globals.ITERATION_FOLDER_NAME}/{current_debug_iteration}"
    create_folder(current_iteration_folder_path)
    get_iterate_code(
        problem,
        task,
        task_code_folder_path,
        current_iteration_folder_path,
        globals.design_hypothesis,
    )
    return (
        jsonify(
            {
                "message": "Debugged and regenerated code",
                "current_iteration": globals.task_map[task_id][
                    globals.CURRENT_DEBUG_ITERATION
                ],
            }
        ),
        200,
    )


@app.route("/get_test_cases_per_lock_step", methods=["GET"])
def get_test_cases_per_lock_step():
    print("calling get_test_cases_per_lock_step...")
    task_id = int(request.args.get("task_id"))
    index = task_id - 1
    task = globals.plan[index]["task"]
    test_cases = test_code_per_lock_step(task, globals.design_hypothesis)
    return (
        jsonify(
            {
                "message": f"Grabbed test cases for {task_id} {task}",
                "test_cases": json.loads(test_cases),
            }
        ),
        200,
    )


# For testing only. Run curl http://127.0.0.1:5000/set_globals_for_uuid/uuid
@app.route("/set_globals_for_uuid/<generated_uuid>", methods=["GET"])
def set_globals_for_uuid(generated_uuid):
    # backend/generated/generations_2024-07-11_11-34-47_321a5bcc-953c-4fed-abd6-53ad7daae446
    print("calling set_globals_for_uuid")
    globals.folder_path = f"{globals.GENERATED_FOLDER_PATH}/{generated_uuid}"
    globals.faked_data = read_file(
        f"{globals.folder_path}/{globals.FAKED_DATA_FILE_NAME}"
    )
    globals.design_hypothesis = read_file(
        f"{globals.folder_path}/{globals.DESIGN_HYPOTHESIS_FILE_NAME}"
    )
    globals.prompt = read_file(f"{globals.folder_path}/{globals.USER_INPUT_FILE_NAME}")
    plan = read_file(f"{globals.folder_path}/{globals.PLAN_FILE_NAME}")
    globals.plan = json.loads(plan)
    globals.theories = json.loads(f"{globals.folder_path}/{globals.THEORIES_FILE_NAME}")
    globals.selected_theories = json.loads(
        f"{globals.folder_path}/{globals.SELECTED_THEORIES_FILE_NAME}"
    )
    task_map = json.loads(
        read_file(f"{globals.folder_path}/{globals.TASK_MAP_FILE_NAME}")
    )
    globals.task_map = {int(key): value for key, value in task_map.items()}
    return jsonify({"message": "Successfully set global fields"}), 200


# Running app
if __name__ == "__main__":
    app.run(debug=True)
