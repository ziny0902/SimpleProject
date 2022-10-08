#!/usr/bin/env python3
from kivy.graphics import Mesh, RenderContext, Callback
from kivy.graphics.opengl import  glEnable, glDisable, glDepthFunc,  GL_LESS, GL_DEPTH_TEST
from kivy.graphics.opengl import glBlendFunc, GL_ONE, GL_ONE_MINUS_SRC_ALPHA,\
                                GL_SRC_ALPHA
from util import *

class Renderer3D():
    vs_src = '''
    #version 400
    precision highp float;
    uniform mat4 projection_mat;
    uniform mat4 modelview_mat;
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
		vec4 pos = modelview_mat * vec4(IN_pos,  1);
		gl_Position = projection_mat * pos;
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
        float f_alpha = smoothstep(1.0 -2* f_width, 1.0, 1 - f_closest_edge); // calculate alpha
        float mask= smoothstep(-1, 2*f_width - 1, -1*f_closest_edge); 
	    vec4 color = frac_color + (frac_lineColor - frac_color*frac_lineColor.a)*f_alpha;
        OUT_color = color*mask;
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
        self.renderer = RenderContext(compute_normal_mat=True)
        self.renderer.shader.vs = self.vs_src
        self.renderer.shader.fs = self.fs_src
        from kivy.graphics.transformation import Matrix
        self.modelview_mat = Matrix().translate(0, 0, -2) 


    def drawTriangle(self, a, b, c, fcolor, lcolor):
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

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        # need for proper rendering
        glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
        pass

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)
        # kivy default blend function value
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pass
    def setup_projection(self, width, height):
        from kivy.graphics.transformation import Matrix
        asp = width / float(height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.renderer['projection_mat'] = proj

    ##
    # angle : degree
    ##
    def rotate(self, angle:float, axis:list):
        self.modelview_mat.rotate((2*angle*3.14)/360, axis[0], axis[1], axis[2])
        self.renderer["modelview_mat"]=self.modelview_mat


    def flush(self):
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
        self.modelview_mat.rotate((2*1*3.14)/360, 1, 1, 1)
        self.renderer["modelview_mat"]=self.modelview_mat
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
