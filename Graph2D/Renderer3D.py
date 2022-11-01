#!/usr/bin/env python3
from kivy.graphics import Mesh, RenderContext, Callback
from kivy.graphics.opengl import  glEnable, glDisable, glDepthFunc, glCullFace, glFrontFace,\
                                GL_LESS, GL_DEPTH_TEST, GL_CULL_FACE, GL_BACK, GL_CCW
# from kivy.graphics.opengl import glBlendFunc, GL_ONE, GL_ONE_MINUS_SRC_ALPHA,\
#                                 GL_SRC_ALPHA
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
    plane_vs = '''
    #version 410
    #extension GL_KHR_vulkan_glsl : enable
    uniform mat4 projection_mat;
    uniform mat4 modelview_mat;
    uniform mat4 lookat;
	in vec3 IN_pos;
    layout (location=0) out vec2 uv;
    void main() {
        vec3 pos = IN_pos * 100.;
        pos.y = -1.;
        gl_Position = projection_mat * lookat * modelview_mat * vec4(pos, 1.0);
        uv = pos.xz;
    }
    '''
    plane_fs = '''
    #version 410
    layout (location=0) in vec2 uv;
    out vec4 outColor;
    // extents of grid in world coordinates
    float gridSize = 100.0;

    // size of one cell
    float gridCellSize = 0.05;

    // color of thin lines
    vec4 gridColorThin = vec4(0.5, 0.5, 0.5, 0.6);

    // color of thick lines (every tenth line)
    vec4 gridColorThick = vec4(1.0, 1.0, 1.0, 0.8);

    // minimum number of pixels between cell lines before LOD switch should occur. 
    const float gridMinPixelsBetweenCells = 4.0;
    float log10(float x)
    {
	    return log(x) / log(10.0);
    }

    float satf(float x)
    {
	    return clamp(x, 0.0, 1.0);
    }

    vec2 satv(vec2 x)
    {
	    return clamp(x, vec2(0.0), vec2(1.0));
    }

    float max2(vec2 v)
    {
	    return max(v.x, v.y);
    }

    vec4 gridColor(vec2 uv)
    {
	    vec2 dudv = vec2(
		    length(vec2(dFdx(uv.x), dFdy(uv.x))),
		    length(vec2(dFdx(uv.y), dFdy(uv.y)))
	    );

	    // LOD : level of detail

	    float lodLevel = max(0.0, log10((length(dudv) * gridMinPixelsBetweenCells) / gridCellSize) + 1.0);
	    float lodFade = fract(lodLevel);

	    // cell sizes for lod0, lod1 and lod2
	    float lod0 = gridCellSize * pow(10.0, floor(lodLevel));
	    float lod1 = lod0 * 10.0;
	    float lod2 = lod1 * 10.0;

	    // each anti-aliased line covers up to 4 pixels
	    dudv *= 4.0;

	    // calculate absolute distances to cell line centers for each lod and pick max X/Y to get coverage alpha value
	    float lod0a = max2( vec2(1.0) - abs(satv(mod(uv, lod0) / dudv) * 2.0 - vec2(1.0)) );
	    float lod1a = max2( vec2(1.0) - abs(satv(mod(uv, lod1) / dudv) * 2.0 - vec2(1.0)) );
	    float lod2a = max2( vec2(1.0) - abs(satv(mod(uv, lod2) / dudv) * 2.0 - vec2(1.0)) );

	    // blend between falloff colors to handle LOD transition
	    vec4 c = lod2a > 0.0 ? gridColorThick : lod1a > 0.0 ? mix(gridColorThick, gridColorThin, lodFade) : gridColorThin;
	    if( abs(uv.y) <= dudv.y && lod2a > 0.0) c = vec4(24./255, 156./255, 1.0, 1.0);
	    if( abs(uv.x) <= dudv.x  && lod2a > 0.0) c = vec4(1.0, 3./255, 3./255, 1.0);

	    // calculate opacity falloff based on distance to grid extents
	    float opacityFalloff = (1.0 - satf(length(uv) / gridSize));

	    // blend between LOD level alphas and scale with opacity falloff
	    c.a *= (lod2a > 0.0 ? lod2a : lod1a > 0.0 ? lod1a : (lod0a * (1.0-lodFade))) * opacityFalloff;

	    return c;
    }
    void main() {
        outColor =  gridColor(uv);
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
        self.layer:list = []
        self.renderer = RenderContext(compute_normal_mat=True)
        self.renderer.shader.vs = self.vs_src
        self.renderer.shader.fs = self.fs_src
        self.plane_renderer = RenderContext()
        self.plane_renderer.shader.vs = self.plane_vs
        self.plane_renderer.shader.fs = self.plane_fs
        self.setup_camera([0, 0, 2], [0, 0, 0], [0, 1, 0])
        self.setup_projection(60, 680, 480, 0.1, 100)
        self.modelview_mat = Matrix()
        self.option = {
                "grid": True,
                "depth_test": True
                }

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
        self.drawCone(tcp, [size[0]*4, size[0]*6], fillColor, lineColor, dir, 10)

    def drawSphere(self, center, size, fillColor, lineColor, density:int = 20):
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
        length = len(indices)
        for i in range(0, length, 3):
            self.drawTriangle( 
                    vertices[ indices[i]   ],
                    vertices[ indices[i+1] ],
                    vertices[ indices[i+2] ],
                    fillColor,
                    lineColor, size, t)

    def drawCubeOutline(self, center, size, lineColor):
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
        half = np.array(size)*0.5
        #front left bottom #0
        f_lb= np.array([-1, -1, -1 ])*half + t
        #front left top #1
        f_lt= np.array([-1, 1, -1 ])*half + t
        #front right top #2
        f_rt= np.array([1, 1, -1 ])*half + t 
        #front right bottom #3 
        f_rb= np.array([1, -1, -1 ])*half + t 
        #back left bottom #4
        b_lb= np.array([-1, -1, 1 ])*half + t 
        #front left top #5
        b_lt= np.array([-1, 1, 1 ])*half + t 
        #front right top #6
        b_rt= np.array([1, 1, 1 ])*half + t 
        #front right bottom #7 
        b_rb= np.array([1, -1, 1 ])*half + t 
        indices=[ 
            # front
          Etag.f_lb.value, Etag.f_lt.value, Etag.f_rt.value,
          Etag.f_rb.value, Etag.f_lb.value,
          # back
          Etag.b_lb.value, Etag.b_lt.value, Etag.b_rt.value,
          Etag.b_rb.value, Etag.b_lb.value,
          
          #side R
          Etag.f_rb.value, Etag.f_rt.value, Etag.b_rt.value,
          Etag.b_rb.value, Etag.f_rb.value,

          #side L
          Etag.f_lb.value, Etag.b_lb.value, Etag.b_lt.value,
          Etag.f_lt.value, Etag.f_lb.value,

          # top
          Etag.f_lt.value, Etag.b_lt.value, Etag.b_rt.value,
          Etag.f_rt.value, Etag.f_lt.value,

          #bottom
          Etag.f_lb.value, Etag.b_lb.value, Etag.b_rb.value,
          Etag.f_rb.value, Etag.f_lb.value
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
        for i in range(0, length, 5):
            pt = []
            for j in range(0, 5):
                pt.append( list(vertices[ indices[i+j] ]) )
            self.drawLinestrip(pt, lineColor)
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
        half = np.array(size)*0.5
        #front left bottom #0
        f_lb= np.array([-1, -1, -1 ])*half + t
        #front left top #1
        f_lt= np.array([-1, 1, -1 ])*half + t
        #front right top #2
        f_rt= np.array([1, 1, -1 ])*half + t 
        #front right bottom #3 
        f_rb= np.array([1, -1, -1 ])*half + t 
        #back left bottom #4
        b_lb= np.array([-1, -1, 1 ])*half + t 
        #front left top #5
        b_lt= np.array([-1, 1, 1 ])*half + t 
        #front right top #6
        b_rt= np.array([1, 1, 1 ])*half + t 
        #front right bottom #7 
        b_rb= np.array([1, -1, 1 ])*half + t 
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


    def setup_gl_context(self, *args):
        if self.option["depth_test"]:
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)
        # glFrontFace(GL_CCW)
        # need for proper rendering
        # glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
        pass

    def reset_gl_context(self, *args):
        if self.option["depth_test"]:
            glDisable(GL_DEPTH_TEST)
        # glDisable(GL_CULL_FACE)
        # kivy default blend function value
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pass
    ##
    # c: camera, t: target
    ##
    def setup_camera(self, c:list, t:list, up:list):
        lookat = Matrix().look_at(c[0], c[1], c[2], t[0], t[1], t[2],  up[0], up[1], up[2])
        self.renderer['lookat'] = lookat
        self.plane_renderer['lookat'] = lookat

    def setup_projection(self, pov:float, width, height, rear:float, far:float):
        asp = width / float(height)
        perspective = Matrix()
        perspective.perspective(pov, asp, rear, far)
        self.renderer['projection_mat'] = perspective
        self.plane_renderer['projection_mat'] = perspective

    ##
    # angle : degree
    ##
    from multipledispatch import dispatch
    @dispatch(list)
    def rotate(self, angle:list):
        m = Matrix()
        m.rotate(math.radians(angle[0]), 1, 0, 0)
        m.rotate(math.radians(angle[1]), 0, 1, 0)
        m.rotate(math.radians(angle[2]), 0, 0, 1)
        self.renderer["modelview_mat"]=m
    @dispatch(float, list)
    def rotate(self, angle:float, axies:list):
        m = self.modelview_mat.rotate(math.radians(angle), axies[0], axies[1], axies[3])
        self.renderer["modelview_mat"] = m

    def translate(self, x:float, y:float, z:float):
        self.modelview_mat.translate(x, y, z)
        self.renderer["modelview_mat"]=self.modelview_mat

    def scale(self, x:float, y:float, z:float):
        m = self.modelview_mat.scale(x, y, z)
        self.renderer["modelview_mat"] = m
    def reset_modelview(self):
        self.modelview_mat = Matrix()

    def flush(self):
        self.renderer.clear()
        if len(self.vertexes_list) <= 0 and len(self.linestrip_list) <= 0:
            return

        # infinite grid
        self.plane_renderer.clear()
        if self.option["grid"] :
            with self.plane_renderer:
                Mesh(
                    vertices = [1., 0., 1., -1., 0., -1., -1., 0., 1., -1., 0., -1., 1., 0., 1., 1., 0., -1.  ],
                    indices = [0, 1, 2, 3, 4, 5],
                    fmt=[ (b'IN_pos', 3, 'float') ],
                    mode='triangles',
                    )
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
        self.linestrip_list.clear()
        ##
        # polygon
        ##
        if len(self.vertexes_list) <= 0 : return
        vertices=[]
        indices=[]
        num_of_vertexes = len(self.vertexes_list)
        vidx = 0
        while vidx < num_of_vertexes:
            # for vertexes in self.vertexes_list:
            while vidx < num_of_vertexes:
                vertexes = self.vertexes_list[vidx]
                base = int(len(vertices)/8)
                if base > 32768: break  
                vertices +=  vertexes['vertices']
                for i in vertexes['indices']:
                    indices.append(i+base)
                vidx += 1
            if len(vertices) > 0 :
                with self.renderer:
                    self.cb = Callback(self.setup_gl_context)
                    Mesh(
                        vertices = vertices,
                        indices= indices,
                        fmt=self.attr_layout,
                        mode='triangles',
                        )
                    self.cb = Callback(self.reset_gl_context)
            vertices.clear()
            indices.clear()
        # for vertexes in self.vertexes_list:
        #     with self.renderer:
        #         self.cb = Callback(self.setup_gl_context)
        #         Mesh(
        #             vertices = vertexes['vertices'],
        #             indices= vertexes['indices'],
        #             fmt=self.attr_layout,
        #             mode='triangles',
        #             )
        #         self.cb = Callback(self.reset_gl_context)

        self.vertexes_list.clear()

