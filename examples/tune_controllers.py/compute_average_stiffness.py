import numpy as np
import mujoco_py


import os
import mujoco_py
from gym_kuka_mujoco import kuka_asset_dir
from gym_kuka_mujoco.controllers import (DirectTorqueController, SACTorqueController, RelativeInverseDynamicsController, InverseDynamicsController, ImpedanceController, ImpedanceControllerV2)

def compute_stiffness(controller, sim, qpos, action):
    nq = len(qpos)
    sim.data.qpos[:] = qpos
    sim.forward()
    controller.set_action(action)
    torque_0 = controller.get_torque()

    stiffness = np.zeros((nq, nq)) 
    for i in range(nq):
        # perturb the position
        eps = 1e-6
        d_qpos = np.zeros(nq)
        d_qpos[i] = eps
        sim.data.qpos[:] = qpos + d_qpos
        sim.forward()

        # rest the action
        torque_i = controller.get_torque()
        
        stiffness[:,i] = (torque_i - torque_0)/eps
    
    return stiffness


def compute_average_stiffness_forbenius_norm(controller, sim):
    qpos_min = sim.model.jnt_range[:,0]
    qpos_max = sim.model.jnt_range[:,1]
    stiffnesses = []
    for i in range(100):
        action = controller.action_space.sample()
        qpos = np.random.uniform(qpos_min, qpos_max)
        stiffnesses.append(compute_stiffness(controller, sim, qpos, action))

    norms = [np.linalg.norm(s) for s in stiffnesses]
    return np.mean(norms)
    # return np.mean(stiffnesses, axis=0)

if __name__ == "__main__":
    model_filename = 'full_kuka_mesh_collision.xml'
    model_path = os.path.join(kuka_asset_dir(), model_filename)
    model = mujoco_py.load_model_from_path(model_path)
    sim = mujoco_py.MjSim(model)

    # Direct Torque Controller
    options = dict()
    options["action_scaling"] = 1.
    controller = DirectTorqueController(sim, **options)
    stiffness = compute_average_stiffness_forbenius_norm(controller, sim)

    print("Mean stiffness norm for the DirectTorque controller")
    print(stiffness)   

    # Inverse Dynamics Controller
    options = dict()
    controller = InverseDynamicsController(sim, **options)
    stiffness = compute_average_stiffness_forbenius_norm(controller, sim)
    
    print("Mean stiffness norm for the InverseDynamicsController")
    print(stiffness)   

    # Relative Inverse Dynamics Controller
    options = dict()
    controller = RelativeInverseDynamicsController(sim, **options)
    stiffness = compute_average_stiffness_forbenius_norm(controller, sim)
    
    print("Mean stiffness norm for the RelativeInverseDynamicsController")
    print(stiffness) 

    # Impedance Controller
    options = dict()
    controller = ImpedanceController(sim, **options)
    stiffness = compute_average_stiffness_forbenius_norm(controller, sim)
    
    print("Mean stiffness norm for the ImpedanceController")
    print(stiffness)   

    # Impedance Controller v2
    options = dict()
    controller = ImpedanceControllerV2(sim, **options)
    stiffness = compute_average_stiffness_forbenius_norm(controller, sim)
    
    print("Mean stiffness norm for the ImpedanceControllerV2")
    print(stiffness)   
    # c
    # import pdb; pdb.set_trace()
        # controller = RelativeInverseDynamicsController(sim)