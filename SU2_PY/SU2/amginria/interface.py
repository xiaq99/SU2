import os, sys
import _amgio as amgio
import numpy as np
import pyamg


def return_mesh_size(mesh):
    
    elt_key  = ['xy', 'xyz',  'Triangles', 'Edges', 'Tetrahedra']
    elt_name = {'xy':'vertices', 'xyz':'vertices',  'Triangles':'triangles', 'Edges':'edges', 'Tetrahedra':'tetrahedra'}
    
    tab_out = []
        
    for elt in elt_key:
        
        if elt not in mesh: continue
        
        nbe = len(mesh[elt])
        
        if nbe > 0:
            tab_out.append("%d %s" % (nbe, elt_name[elt]))
    
    return ', '.join(map(str, tab_out))
    

def amg_call(config):
    
    cmd = ''
    cmd = "amg -in %s -sol %s -p 1 \
         -c %f -hgrad %.2f -hmin %le -hmax %le -out %s \
        -itp  %s  -nordg " \
        % (config['mesh_in'], config['sol_in'],  \
        config['size'],  config['hgrad'], config['hmin'], config['hmax'], \
        config['mesh_out'], config['sol_itp_in'])
        
    if config['adap_source'] != "":
        cmd += ' -source %s ' % config['adap_source']
    
    if config['adap_back'] != "":
        cmd += ' -back %s ' % config['adap_back']
    
    cmd += ' > %s' % config['amg_log']
    os.system(cmd)


def amg_call_met(config):
    
    cmd = ''
    cmd = "amg -in %s -met %s \
        -hgrad %.2f -hmin %le -hmax %le -out %s \
        -itp  %s  -nordg " \
        % (config['mesh_in'], config['sol_in'],  \
        config['hgrad'], config['hmin'], config['hmax'], \
        config['mesh_out'], config['sol_itp_in'])
            
    cmd += ' > %s' % config['amg_log']
    os.system(cmd)


def amg_call_python(mesh, config):
    
    remesh_options                = {}

    remesh_options['Lp']          = config['Lp']
    remesh_options['gradation']   = config['hgrad']
    remesh_options['logfile']     = config['amg_log']
    remesh_options['options']     = config['options']
    
    Dim = mesh['dimension']
    
    if Dim == 2 :
        Ver = mesh['xyz']
        mesh['xy'] = np.stack((Ver[:,0],Ver[:,1]), axis=1)
        
        del mesh['xyz']
    
    ''' 
      TO ADD: 
     {'adap_back' 'hmax' 'hmin'
      'sol_in': 'current_sensor.solb', 'sol_itp_in': 'current.solb', 'metric_in': '', 'adap_source': '', 
     'mesh_in': 'current.meshb', 'mesh_out': 'current.new.meshb'}
    ''' 
    
    
    if 'xy' in mesh:    mesh['xy']  = mesh['xy'].tolist()
    if 'xyz' in mesh:   mesh['xyz'] = mesh['xyz'].tolist()
    
    if 'Edges' in mesh:      mesh['Edges']      = mesh['Edges'].tolist() 
    if 'Triangles' in mesh:  mesh['Triangles']  = mesh['Triangles'].tolist()
    if 'Tetrahedra' in mesh: mesh['Tetrahedra'] = mesh['Tetrahedra'].tolist()   

    if 'sensor' in mesh: mesh['sensor'] = mesh['sensor'].tolist()
    if 'metric' in mesh: mesh['metric'] = mesh['metric'].tolist()
    
    try:
        mesh_new = pyamg.adapt_mesh(mesh, remesh_options)        
    except:
        sys.stderr("## ERROR : pyamg failed.\n")
        raise
    
    return mesh_new
    
    
# --- Read mesh using amgio module
def read_mesh(mesh_name, solution_name):
    
    Ver = []
    Tri = []
    Tet = []
    Edg = []
    Hex = []
    Pyr = []
    Pri = []
    Qua = []
    Sol = []
    SolTag = []
    
    Markers = []
    
    amgio.py_ReadMesh(mesh_name, solution_name, Ver, Tri, Tet, Edg, Hex, Qua, Pyr, Pri, Sol, SolTag,  Markers)
        
    NbrTet = len(Tet)/5
    Tet = np.reshape(Tet,(NbrTet, 5)).astype(int)
    
    NbrTri = len(Tri)/4
    Tri = np.reshape(Tri,(NbrTri, 4)).astype(int)
    
    NbrEdg = len(Edg)/3
    Edg = np.reshape(Edg,(NbrEdg, 3)).astype(int)

    NbrVer = len(Ver)/3
    Ver = np.reshape(Ver,(NbrVer, 3))
    
    SolSiz = len(Sol)/NbrVer
    Sol = np.array(Sol).reshape(NbrVer,SolSiz).tolist()
    
    # First row of Markers contains dimension
    Dim = int(Markers[0])
    
    mesh = dict()
    
    mesh['dimension']    = Dim
    
    mesh['xyz']          = Ver 
    
    mesh['Triangles']    = Tri
    mesh['Tetrahedra']   = Tet
    mesh['Edges']        = Edg
    mesh['Corners']      = []
    mesh['solution']     = Sol
    
    mesh['solution_tag'] = SolTag
    
    mesh['id_solution_tag'] = dict()
    for i in range(len(SolTag)):
        mesh['id_solution_tag'][SolTag[i]] = i
        
    mesh['markers'] = Markers    
    
    return mesh
    

def write_mesh(mesh_name, solution_name, mesh):
    
    Tri     = []
    Tet     = []
    Edg     = []
    Hex     = []
    Pyr     = []
    Pri     = []
    Qua     = []
    Sol     = []
    Markers = []
    Dim     = 3
    Ver     = []
    SolTag  = []
        
    if 'Triangles' in mesh:     Tri     = mesh['Triangles']
    if 'Tetrahedra' in mesh:    Tet     = mesh['Tetrahedra']
    if 'Edges' in mesh:         Edg     = mesh['Edges']
    if 'solution' in mesh:      Sol     = mesh['solution']
    if 'markers' in mesh:       Markers = mesh['markers']
    if 'dimension' in mesh:     Dim     = mesh['dimension']
    if 'solution_tag' in mesh:  SolTag  = mesh['solution_tag']
    if 'xyz' in mesh:
        Ver = mesh['xyz']
        Ver = np.array(Ver).reshape(3*len(Ver)).tolist()
    elif 'xy' in mesh:
        Ver = np.array(mesh['xy'])
        z = np.zeros(len(mesh['xy']))
        Ver = np.c_[Ver, z]
        Ver = np.array(Ver).reshape(3*len(Ver)).tolist()
    
    Tri = np.array(Tri).reshape(4*len(Tri)).tolist()
    Tet = np.array(Tet).reshape(5*len(Tet)).tolist()
    Edg = np.array(Edg).reshape(3*len(Edg)).tolist()
    
    if len(Sol) > 1 :
        SolSiz = len(Sol[1])
        Sol = np.array(Sol).reshape(SolSiz*len(Sol)).tolist() 
    else:
        Sol = []
    
    amgio.py_WriteMesh(mesh_name, solution_name, Ver, Tri, Tet, Edg, Hex, Qua, Pyr, Pri, Sol, SolTag, Markers, Dim)
    

def write_solution(solution_name, solution):
    
    Dim     = solution['dimension']
    Sol     = solution['solution']
    
    Ver = solution['xyz']
    
    solution_tag = solution['solution_tag']
    
    NbrVer = len(Ver)
    Ver = np.array(Ver).reshape(3*len(Ver)).tolist()
    
    if len(Sol) > 1 :
        SolSiz = len(Sol[1])
        Sol = np.array(Sol).reshape(SolSiz*len(Sol)).tolist()
    else:
        sys.stderr.write("## ERROR write_solution : No solution.\n")
        sys.exit(1)
        
    amgio.py_WriteSolution(solution_name, Ver, Sol, solution_tag, NbrVer, Dim)


def create_sensor(solution, sensor):
    
    Ver = solution['xyz']
    
    NbrVer = len(Ver)
    Ver = np.array(Ver).reshape(3*len(Ver)).tolist()
    
    Dim = solution['dimension']
    Sol = np.array(solution['solution'])
    
    if sensor == "MACH":
        
        iMach = solution['id_solution_tag']['Mach']
        sensor = Sol[:,iMach]
        sensor = np.array(sensor).reshape((len(sensor),1))
        sensor_header = ["Mach"]
        
    elif sensor == "PRES":
        
        iPres = solution['id_solution_tag']['Pressure']
        sensor = Sol[:,iPres]
        sensor = np.array(sensor).reshape((len(sensor),1))        
        sensor_header = ["Pres"]
        
    elif sensor == "MACH_PRES":

        iPres  = solution['id_solution_tag']['Pressure']
        iMach  = solution['id_solution_tag']['Mach']
        mach   = np.array(Sol[:,iMach])
        pres   = np.array(Sol[:,iPres])
        sensor = np.stack((mach, pres), axis=1)    
        sensor_header = ["Mach", "Pres"]

    elif sensor == "GOAL":

        if Dim == 2:
            sensor = Sol[:,-3:]
            sensor = np.array(sensor).reshape((len(sensor),3))
        elif Dim == 3:
            sensor = Sol[:,-6:]
            sensor = np.array(sensor).reshape((len(sensor),6))
        sensor_header = ["Goal"]
                
    else :
        sys.stderr.write("## ERROR : Unknown sensor.\n")
        sys.exit(1)
    
    sensor_wrap = dict()
    
    sensor_wrap['solution_tag'] = sensor_header
    sensor_wrap['xyz'] = solution['xyz']
    
    sensor_wrap['dimension']    = solution['dimension']
    sensor_wrap['solution']     = sensor
    
    return sensor_wrap

