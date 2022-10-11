#!/usr/bin/env python3
from kivy.graphics import Mesh, RenderContext, Callback
from kivy.graphics.opengl import  glEnable, glDisable, glDepthFunc, glCullFace, glFrontFace,\
                                GL_LESS, GL_DEPTH_TEST, GL_CULL_FACE, GL_BACK, GL_CCW
from kivy.graphics.opengl import glBlendFunc, GL_ONE, GL_ONE_MINUS_SRC_ALPHA,\
                                GL_SRC_ALPHA
from util import *
import math
import numpy as np
from enum import Enum, auto

from kivy.graphics.transformation import Matrix

class Renderer3D():
    vs_src = '''
    #version 400
    precision highp float;
    uniform mat4 projection_mat;
    uniform mat4 modelview_mat;
    uniform mat4 lookat;
	in vec3 IN_pos;
	in float IN_color;
	in vec3 IN_barycentric;
	in float IN_lineColor;
	out vec3 frac_barycentric;
	out vec4 frac_color;
	out vec4 frac_lineColor;

    vec4 EncodeFloatRGBA( float v )
    {
        uint rgba = (floatBitsToUint(v));
        float r = float(rgba >> 24) / 255.0;
        float g = float((rgba & 0x00ff0000) >> 16) / 255.0;
        float b = float((rgba & 0x0000ff00) >> 8) / 255.0;
        float a = float(rgba & 0x000000ff) / 255.0;
        return vec4(r, g, b, a);
    }

	void main(){
		vec4 pos = projection_mat * lookat * modelview_mat * vec4(IN_pos,  1);
		gl_Position = pos;
		frac_color = EncodeFloatRGBA( IN_color );
		frac_lineColor = EncodeFloatRGBA( IN_lineColor );
		frac_barycentric = IN_barycentric;
	}
    '''
    fs_src = '''
    #version 330
    precision highp float;
	out vec4 OUT_color;
	in vec3 frac_barycentric;
	in vec4 frac_color;
	in vec4 frac_lineColor;

	void main(){
	    float f_closest_edge = min(frac_barycentric.x,
        min(frac_barycentric.y, frac_barycentric.z)); // see to which edge this pixel is the closest
        float f_width = fwidth(f_closest_edge); // calculate derivative (divide f_thickness by this to have the line width constant in screen-space)
        float f_alpha = smoothstep(1.0 - f_width, 1.0, 1 - f_closest_edge); // calculate alpha
	    vec4 color = frac_color + (frac_lineColor - frac_color*frac_lineColor.a)*f_alpha;
        OUT_color = color;
	}
    '''
    attr_layout = [
        (b'IN_pos', 3, 'float'),
        (b'IN_color', 1, 'float'),
        (b'IN_barycentric', 3, 'float'),
        (b'IN_lineColor', 1, 'float'),
    ]
    def __init__(self, **kwargs):
        self.vertexes_list:list = []
        self.linestrip_list:list = []
        self.renderer = RenderContext(compute_normal_mat=True)
        self.renderer.shader.vs = self.vs_src
        self.renderer.shader.fs = self.fs_src
        self.setup_camera([0, 0, 2], [0, 0, 0], [0, 1, 0])
        self.setup_projection(60, 680, 480, 0.1, 100)
        self.modelview_mat = Matrix()


    ##
    # size : R, height
    # dir : direction vector
    ##
    def drawCone(self, center:list, size:list, fillColor:list, lineColor:list, dir:list=[0, 1, 0], density:int= 10):
        t= np.array(center)
        angle:float = rectangular_to_spherical(dir)
        angle[1] = -angle[1]
        angle[2] = math.pi/2 - angle[2]
        R = Matrix()
        R.rotate(angle[1], 0, 0, 1)
        R.rotate(angle[2], 0, 1, 0)
        R = np.delete( np.array(R.tolist()), 3, 1 )
        R = np.delete( R, 3, 0)

        cp = np.array([1, 0, 0])  * size[1] 
        bcp = np.array([0, 0, 0] )
        cp  = np.matmul(R, cp.T)  + t
        bcp = np.matmul(R, bcp.T) + t
        unit_step = 2*math.pi/(density)
        for i in range(0, density) :
            p1 = np.array([0, math.sin(i*unit_step), math.cos(i*unit_step)]) * size[0]
            p2 = np.array([0, math.sin((i+1)*unit_step), math.cos((i+1)*unit_step)]) * size[0]
            p1 = np.matmul(R,p1.T) + t
            p2 = np.matmul(R,p2.T) + t
            self.drawTriangle( 
                    cp,
                    p2,
                    p1,
                    fillColor,
                    lineColor, size, t)
            self.drawTriangle( 
                    bcp,
                    p1,
                    p2,
                    fillColor,
                    lineColor, size, t)

    def drawCylinder(self, center:list, size:list, fillColor:list, lineColor:list, dir:list=[0, 1, 0], density:int= 10):
        t= np.array(center)
        angle:float = rectangular_to_spherical(dir)
        angle[1] = -angle[1]
        angle[2] = math.pi/2 - angle[2]
        R = Matrix()
        R.rotate(angle[1], 0, 0, 1)
        R.rotate(angle[2], 0, 1, 0)
        R = np.delete( np.array(R.tolist()), 3, 1 )
        R = np.delete( R, 3, 0)
        tcp = np.array([1, 0, 0])  * size[1] 
        bcp = np.array([0, 0, 0]) 
        tcp = np.matmul(R, tcp.T) + t
        bcp = np.matmul(R, bcp.T) + t
        unit_step = 2*math.pi/(density)
        for i in range(0, density) :
            p1 = np.array([0, math.sin(i*unit_step), math.cos(i*unit_step)]) * size[0]
            p2 = np.array([0, math.sin((i+1)*unit_step), math.cos((i+1)*unit_step)]) * size[0]
            p3 = p1 + np.array([1, 0, 0]) * size[1]
            p4 = p2 + np.array([1, 0, 0]) * size[1]
            p1 = np.matmul(R, p1.T) + t
            p2 = np.matmul(R, p2.T) + t
            p3 = np.matmul(R, p3.T) + t
            p4 = np.matmul(R, p4.T) + t
            self.drawTriangle( 
                    p3,
                    p2,
                    p1,
                    fillColor,
                   lineColor, size, t)
            self.drawTriangle( 
                    p2,
                    p3,
                    p4,
                    fillColor,
                   lineColor, size, t)
            self.drawTriangle( 
                    bcp,
                    p1,
                    p2,
                    fillColor,
                   lineColor, size, t)
            self.drawTriangle( 
                    tcp,
                    p4,
                    p3,
                    fillColor,
                    lineColor, size, t)
    def drawArrow(self, center:list, size:list, fillColor:list, lineColor:list, dir:list=[0, 1, 0], density:int= 10):
        t= np.array(center)
        angle:float = rectangular_to_spherical(dir)
        angle[1] = -angle[1]
        angle[2] = math.pi/2 - angle[2]
        R = Matrix()
        R.rotate(angle[1], 0, 0, 1)
        R.rotate(angle[2], 0, 1, 0)
        R = np.delete( np.array(R.tolist()), 3, 1 )
        R = np.delete( R, 3, 0)
        tcp = np.array([1, 0, 0])  * size[1] 
        bcp = np.array([0, 0, 0]) 
        tcp = np.matmul(R, tcp.T) + t
        bcp = np.matmul(R, bcp.T) + t
        unit_step = 2*math.pi/(density)
        for i in range(0, density) :
            p1 = np.array([0, math.sin(i*unit_step), math.cos(i*unit_step)]) * size[0]
            p2 = np.array([0, math.sin((i+1)*unit_step), math.cos((i+1)*unit_step)]) * size[0]
            p3 = p1 + np.array([1, 0, 0]) * size[1]
            p4 = p2 + np.array([1, 0, 0]) * size[1]
            p1 = np.matmul(R, p1.T) + t
            p2 = np.matmul(R, p2.T) + t
            p3 = np.matmul(R, p3.T) + t
            p4 = np.matmul(R, p4.T) + t
            self.drawTriangle( 
                    p3,
                    p2,
                    p1,
                    fillColor,
                   lineColor, size, t)
            self.drawTriangle( 
                    p2,
                    p3,
                    p4,
                    fillColor,
                   lineColor, size, t)
            self.drawTriangle( 
                    bcp,
                    p1,
                    p2,
                    fillColor,
                   lineColor, size, t)
            self.drawTriangle( 
                    tcp,
                    p4,
                    p3,
                    fillColor,
                    lineColor, size, t)
        self.drawCone(tcp, [size[0]*2, size[0]*2], fillColor, lineColor, dir, 10)

    def drawSphere(self, center, size, fillColor, lineColor, density:int = 40):
        t = np.array(center)
        unit_step = math.pi/density
        #
        # spe
        #  |
        # sps
        #
        for j in np.arange(-density/2, density/2 ):
            sps = np.array([ 0, math.sin(j*unit_step), math.cos(j*unit_step) ])
            spe = np.array([ 0, math.sin((j+1) * unit_step), math.cos((j+1) * unit_step) ])
            #
            # p2---p4
            # |    |
            # p1---p3
            #
            for i in np.arange(0, 2*density):
                p1 = np.array([sps[2]*math.sin(i*unit_step), sps[1], sps[2]*math.cos(i*unit_step)]) * size[0] + t
                p2 = np.array([spe[2]*math.sin(i*unit_step), spe[1], spe[2]*math.cos(i*unit_step)]) * size[0] + t
                p3 = np.array([sps[2]*math.sin((i+1)*unit_step), sps[1], sps[2]*math.cos((i+1)*unit_step)]) * size[0] + t
                p4 = np.array([spe[2]*math.sin((i+1)*unit_step), spe[1], spe[2]*math.cos((i+1)*unit_step)]) * size[0] + t
                self.drawTriangle( 
                        p1,
                        p4,
                        p2,
                        fillColor,
                       lineColor, size, t)
                self.drawTriangle( 
                        p1,
                        p3,
                        p4,
                        fillColor,
                       lineColor, size, t)

    def drawPyramid(self, center, size, fillColor, lineColor, dir:list=[0, 1, 0]):
        class Etag(Enum):
            cp = 0
            lt = auto()
            lb = auto()
            rt = auto()
            rb = auto()

        t= np.array(center)

        angle:float = rectangular_to_spherical(dir)
        angle[1] = -angle[1]
        angle[2] = math.pi/2 - angle[2]
        R = Matrix()
        R.rotate(angle[1], 0, 0, 1)
        R.rotate(angle[2], 0, 1, 0)
        R = np.delete( np.array(R.tolist()), 3, 1 )
        R = np.delete( R, 3, 0)

        cp = np.array([1, 0, 0])  *size
        lt = np.array([0, 1, -1]) *size
        lb = np.array([0, -1, -1])*size
        rt = np.array([0, 1, 1])  *size
        rb = np.array([0, -1, 1]) *size

        cp = np.matmul(R, cp.T) + t
        lt = np.matmul(R, lt.T) + t
        lb = np.matmul(R, lb.T) + t
        rt = np.matmul(R, rt.T) + t
        rb = np.matmul(R, rb.T) + t

        vertices:list = [ cp, lt, lb, rt, rb ]
        indices:list = [
                Etag.cp.value, Etag.lb.value, Etag.lt.value,
                Etag.cp.value, Etag.rb.value, Etag.lb.value,
                Etag.cp.value, Etag.rt.value, Etag.rb.value,
                Etag.cp.value, Etag.lt.value, Etag.rt.value,
                Etag.lb.value, Etag.rt.value, Etag.lt.value,
                Etag.lb.value, Etag.rb.value, Etag.rt.value,
                ]
        colorlist = [
                [155, 0, 0, 255],
                [0, 155, 0, 255],
                [0, 0, 155, 255],
                [50, 50, 50, 255],
                [155, 155, 155, 255],
                [155, 155, 155, 255],
                ]
        length = len(indices)
        for i in range(0, length, 3):
            self.drawTriangle( 
                    vertices[ indices[i]   ],
                    vertices[ indices[i+1] ],
                    vertices[ indices[i+2] ],
                    fillColor,
                    # colorlist[int(i/3)],
                    lineColor, size, t)

    ##
    # size: width, height, depth
    ##
    def drawCube(self, center, size, fillColor, lineColor):
        class Etag(Enum):
            f_lb = 0
            f_lt = auto()
            f_rt = auto()
            f_rb = auto()
            b_lb = auto()
            b_lt = auto()
            b_rt = auto()
            b_rb = auto()
        
        # translate vector
        t= np.array(center)
        #front left bottom #0
        f_lb= np.array([-1, -1, -1 ])*size + t
        #front left top #1
        f_lt= np.array([-1, 1, -1 ])*size + t
        #front right top #2
        f_rt= np.array([1, 1, -1 ])*size + t 
        #front right bottom #3 
        f_rb= np.array([1, -1, -1 ])*size + t 
        #back left bottom #4
        b_lb= np.array([-1, -1, 1 ])*size + t 
        #front left top #5
        b_lt= np.array([-1, 1, 1 ])*size + t 
        #front right top #6
        b_rt= np.array([1, 1, 1 ])*size + t 
        #front right bottom #7 
        b_rb= np.array([1, -1, 1 ])*size + t 
        indices = \
        [ 
            # front
          Etag.f_lb.value, Etag.f_lt.value, Etag.f_rt.value,
          Etag.f_lb.value, Etag.f_rt.value, Etag.f_rb.value,

          # back
          Etag.b_lb.value, Etag.b_rt.value, Etag.b_lt.value,
          Etag.b_lb.value, Etag.b_rb.value, Etag.b_rt.value,
          
          #side R
          Etag.f_rb.value, Etag.f_rt.value, Etag.b_rt.value,
          Etag.f_rb.value, Etag.b_rt.value, Etag.b_rb.value,

          #side L
          Etag.f_lb.value, Etag.b_lt.value, Etag.f_lt.value,
          Etag.f_lb.value, Etag.b_lb.value, Etag.b_lt.value,

          # top
          Etag.f_lt.value, Etag.b_lt.value, Etag.b_rt.value,
          Etag.f_lt.value, Etag.b_rt.value, Etag.f_rt.value,

          #bottom
          Etag.f_lb.value, Etag.b_rb.value, Etag.b_lb.value,
          Etag.f_lb.value, Etag.f_rb.value, Etag.b_rb.value 
        ] 
        vertices:list =[
            f_lb,
            f_lt,
            f_rt,
            f_rb,
            b_lb,
            b_lt,
            b_rt,
            b_rb,
        ]
        length = len(indices)
        for i in range(0, length, 3):
            self.drawTriangle( 
                    vertices[ indices[i]   ],
                    vertices[ indices[i+1] ],
                    vertices[ indices[i+2] ],
                    fillColor,
                    lineColor, size, t)

    def drawTriangle(self, a, b, c, fcolor, lcolor, scale, translate):
        vertexes = {}
        fc = cpTorgba(fcolor)
        lc = cpTorgba(lcolor)
        vertexes['indices'] = [0, 1, 2]
        vertexes['vertices'] = [
                a[0], a[1], a[2], fc, 1., 0., 0., lc,
                b[0], b[1], b[2], fc, 0., 1.0, 0., lc,
                c[0], c[1], c[2], fc, 0., 0., 1.0, lc
            ]
        self.vertexes_list.append(vertexes)
        vertexes['scale'] = scale
        vertexes['translate'] = translate 

    def drawLinestrip(self, ptlist:list, lineColor:list):
        lc = cpTorgba(lineColor)
        indices:list = []
        vertices:list = []
        i:int = 0
        for v3 in ptlist :
            indices.append(i)
            for pt in v3:
                vertices.append(pt)
            vertices.append(lc)
            vertices.append(1.)
            vertices.append(1.)
            vertices.append(1.)
            vertices.append(lc)
            i += 1
        linestrip = {}
        linestrip['vertices'] = vertices
        linestrip['indices'] = indices
        self.linestrip_list.append(linestrip)
        # length = len(ptlist)
        # for i in range(0, length-1):
        #     p1 = ptlist[i]
        #     p2 = ptlist[i+1]
        #     dir = np.array(p2) - np.array(p1)
        #     norm = np.linalg.norm(dir)
        #     self.drawCylinder( p2, [0.01, norm], lineColor, lineColor, dir, 4)


    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        # need for proper rendering
        # glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
        pass

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        # kivy default blend function value
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pass
    ##
    # c: camera, t: target
    ##
    def setup_camera(self, c:list, t:list, up:list):
        lookat = Matrix().look_at(c[0], c[1], c[2], t[0], t[1], t[2],  up[0], up[1], up[2])
        self.renderer['lookat'] = lookat

    def setup_projection(self, pov:float, width, height, rear:float, far:float):
        asp = width / float(height)
        perspective = Matrix()
        perspective.perspective(pov, asp, rear, far)
        self.renderer['projection_mat'] = perspective

    ##
    # angle : degree
    ##
    def rotate(self, angle:float, axis:list):
        self.renderer["modelview_mat"]=Matrix().rotate(math.radians(angle), axis[0], axis[1], axis[2])
    def rotate_x(self, angle:float ):
        self.modelview_mat.rotate((2*angle*math.pi)/360, 1, 0, 0)
        self.renderer["modelview_mat"]=self.modelview_mat
    def rotate_y(self, angle:float ):
        self.modelview_mat.rotate((2*angle*math.pi)/360, 0, 1, 0)
        self.renderer["modelview_mat"]=self.modelview_mat
    def rotate_z(self, angle:float ):
        self.modelview_mat.rotate((2*angle*math.pi)/360, 0, 0, 1)
        self.renderer["modelview_mat"]=self.modelview_mat
    def translate(self, x:float, y:float, z:float):
        self.modelview_mat.translate(x, y, z)
        self.renderer["modelview_mat"]=self.modelview_mat

    def flush(self):
        from kivy.graphics import PushMatrix, PopMatrix
        from kivy.graphics.context_instructions import Scale , Translate
        self.renderer.clear()
        if len(self.vertexes_list) <= 0:
            return
        ##
        # polygon
        ##
        vertices=[]
        indices=[]
        for vertexes in self.vertexes_list:
            base = int(len(vertices)/8)
            vertices +=  vertexes['vertices']
            for i in vertexes['indices']:
                indices.append(i+base)

        from kivy.graphics import PushMatrix, PopMatrix
        self.renderer.clear()
        for linestrip in self.linestrip_list:
            with self.renderer:
                self.cb = Callback(self.setup_gl_context)
                Mesh(
                    vertices = linestrip['vertices'],
                    indices = linestrip['indices'],
                    fmt=self.attr_layout,
                    mode='line_strip',
                )
                self.cb = Callback(self.reset_gl_context)
        with self.renderer:
            PushMatrix()
            self.cb = Callback(self.setup_gl_context)
            Mesh(
                vertices = vertices,
                indices= indices,
                fmt=self.attr_layout,
                mode='triangles',
                )
            self.cb = Callback(self.reset_gl_context)
            PopMatrix()

        self.vertexes_list.clear()
        self.linestrip_list.clear()

