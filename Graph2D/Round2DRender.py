#!/usr/bin/env python3
from kivy.graphics import Mesh, RenderContext, Callback
from kivy.graphics.opengl import glBlendFunc, GL_ONE, GL_ONE_MINUS_SRC_ALPHA,\
                                GL_SRC_ALPHA
from util import *

class Round2DRender():
    vs_src = '''
    #version 400
    precision highp float;
    uniform vec2       iScreen;
    uniform vec4       iResolution;
    uniform mat4 projection_mat;

	in vec2 IN_pos;
	in vec2 IN_uv;
	in float IN_radius;
	in float IN_fill;
	in float IN_outline;

	out struct {
		vec2 uv;
		vec4 fill;
		vec4 outline;
	} FRAG;

    vec2 get_glcoord(vec2 ipos) {
        vec4 pos = projection_mat * vec4(ipos, 0.0, 1.0);
        return pos.xy;
    }

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
		gl_Position = vec4(get_glcoord(IN_pos+IN_radius*IN_uv), 0.0, 1.0);
		FRAG.uv = IN_uv;
		FRAG.fill = EncodeFloatRGBA(IN_fill);
		FRAG.fill.rgb *= FRAG.fill.a;
		FRAG.outline = EncodeFloatRGBA(IN_outline);
		//FRAG.outline.a *= IN_outline.a;
	}
    '''
    fs_src = '''
    #version 330
    precision highp float;
    uniform vec4       iResolution;
	in struct {
		vec2 uv;
		vec4 fill;
		vec4 outline;
	} FRAG;
	in vec4 gl_FragCoord;
	out vec4 OUT_color;

	void main(){
	    float len = length(FRAG.uv);
	    float fw = length(fwidth(FRAG.uv));
	    float mask = smoothstep(-1, fw - 1,  -len);

	    float outline = 1-fw;
	    float outline_mask = smoothstep(outline - fw, outline, len);
	    vec4 color = FRAG.fill + (FRAG.outline - FRAG.fill*FRAG.outline.a)*outline_mask;
	    OUT_color = color*mask;
	}
    '''
    attr_layout = [
        (b'IN_pos', 2, 'float'),
        (b'IN_uv', 2, 'float'),
        (b'IN_radius', 1, 'float'),
        (b'IN_fill', 1, 'float'),
        (b'IN_outline', 1, 'float'),
    ]
    def __init__(self, **kwargs):
        self.lineScale = 1.0
        self.vertexes_list = []
        self.renderer = RenderContext(use_parent_projection=True)
        self.renderer.shader.vs = self.vs_src
        self.renderer.shader.fs = self.fs_src
    def drawDot(self, size, pos, fillColor):
        r = size*0.5*self.lineScale
        fc = cpTorgba(fillColor)
        vertexes = {}
        vertexes['indices'] = [0, 1, 2, 0, 2, 3]
        vertexes['vertices'] = [
            pos[0], pos[1], -1, -1, r, fc, fc,
            pos[0], pos[1], -1,  1, r, fc, fc,
            pos[0], pos[1],  1,  1, r, fc, fc,
            pos[0], pos[1],  1, -1, r, fc, fc
            ]
        self.vertexes_list.append(vertexes)

    def drawFatSegment(self, a, b, radius, outlineColor, fillColor ):
        r = radius + self.lineScale
        t = vNomalize(vSub(b, a))
        #print('t =', t)
        fc = cpTorgba(fillColor)
        oc = cpTorgba(outlineColor)
        vertexes = {}
        vertexes['indices'] = [0, 1, 2, 1, 2, 3, 2, 3, 4, 3, 4, 5, 4, 5, 6, 5, 6, 7]
        vertexes['vertices'] = [
            float(a[0]), float(a[1]), (-t[0] + t[1]), (-t[0] - t[1]), r, fc, oc,
            float(a[0]), float(a[1]), (-t[0] - t[1]), (+t[0] - t[1]), r, fc, oc,
            float(a[0]), float(a[1]), ( -0.0 + t[1]), (-t[0] + 0.0 ), r, fc, oc,
            float(a[0]), float(a[1]), ( -0.0 - t[1]), (+t[0] + 0.0 ), r, fc, oc,
            float(b[0]), float(b[1]), ( +0.0 + t[1]), (-t[0] - 0.0 ), r, fc, oc,
            float(b[0]), float(b[1]), ( +0.0 - t[1]), (+t[0] - 0.0 ), r, fc, oc,
            float(b[0]), float(b[1]), (+t[0] + t[1]), (-t[0] + t[1]), r, fc, oc,
            float(b[0]), float(b[1]), (+t[0] - t[1]), (+t[0] + t[1]), r, fc, oc,
            ]
        self.vertexes_list.append(vertexes)
    def drawSegment(self, a, b, color):
        self.drawFatSegment(a, b, 0., color, color)

    def drawCircle(self, pos, angle, radius, outlineColor, fillColor):
        fc = cpTorgba(fillColor)
        oc = cpTorgba(outlineColor)
        r = float(radius) + self.lineScale
        x = pos[0]
        y = pos[1]
        vertexes = {}
        vertexes['indices'] = [0, 1, 2, 0, 2, 3]
        vertexes['vertices'] = [
            float(x), float(y), -1., -1., r, fc, oc,
            float(x), float(y), -1.,  1., r, fc, oc,
            float(x), float(y),  1.,  1., r, fc, oc,
            float(x), float(y),  1., -1., r, fc, oc,
            ]
        self.vertexes_list.append(vertexes)
        self.drawSegment(pos, vAdd(pos, vMul(vUnitforangle(angle), 0.75*radius)), outlineColor)

    def drawPolygon(self, count, verts, radius, outlineColor, fillColor):
        # make a list
        indexes = [None] * (12 * count + 3*(count - 2))
        for i in range(0, count - 2):
            indexes[3*i + 0] = 0
            indexes[3*i + 1] = 4*(i + 1)
            indexes[3*i + 2] = 4*(i + 2)
        start = 3*(count - 2)
        for i0 in range(0, count):
            i1 = (i0 + 1)%count
            indexes[start+12*i0 +  0] = 4*i0 + 0;
            indexes[start+12*i0 +  1] = 4*i0 + 1;
            indexes[start+12*i0 +  2] = 4*i0 + 2;
            indexes[start+12*i0 +  3] = 4*i0 + 0;
            indexes[start+12*i0 +  4] = 4*i0 + 2;
            indexes[start+12*i0 +  5] = 4*i0 + 3;
            indexes[start+12*i0 +  6] = 4*i0 + 0;
            indexes[start+12*i0 +  7] = 4*i0 + 3;
            indexes[start+12*i0 +  8] = 4*i1 + 0;
            indexes[start+12*i0 +  9] = 4*i0 + 3;
            indexes[start+12*i0 + 10] = 4*i1 + 0;
            indexes[start+12*i0 + 11] = 4*i1 + 1;
        inset = float(-max(0, 2.*self.lineScale - float(radius)))
        outset = float(radius) + self.lineScale
        r = outset - inset
        vertices = []
        fc = cpTorgba(fillColor)
        oc = cpTorgba(outlineColor)
        for i in range(0, count):
            v0 = verts[i]
            v_prev = verts[(i+(count - 1))%count]
            v_next = verts[(i+(count + 1))%count]
            n1 = vNomalize(vPerp(vSub(v0, v_prev)))
            n2 = vNomalize(vPerp(vSub(v_next, v0)))
            of = vMul(vAdd(n1, n2), 1.0/(vDot(n1, n2)+1.0))
            v = vAdd(v0, vMul(of, inset))
            vertices.extend([v[0], v[1], 0.0, 0.0, 0.0,  fc, oc])
            vertices.extend([v[0], v[1], n1[0], n1[1], r,fc, oc])
            vertices.extend([v[0], v[1], of[0], of[1], r,fc, oc])
            vertices.extend([v[0], v[1], n2[0], n2[1], r,fc, oc])
            #debug
            #print('n1, n2, of:', n1, n2, of)
            #print('v:', v)
        #debug
        # print(vertices)
        # print(indexes)
        #
        vertexes = {}
        vertexes['indices'] = indexes
        vertexes['vertices'] = vertices
        self.vertexes_list.append(vertexes)

    def setup_gl_context(self, *args):
        # need for proper rendering
        glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)

    def reset_gl_context(self, *args):
        # kivy default blend function value
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def flush(self):
        if len(self.vertexes_list) <= 0:
            return
        vertices=[]
        indices=[]
        for vertexes in self.vertexes_list:
            base = int(len(vertices)/7)
            vertices +=  vertexes['vertices']
            for i in vertexes['indices']:
                indices.append(i+base)
        self.renderer.clear()
        with self.renderer:
            # debug
            # print(vertices)
            # print(indices)
            self.cb = Callback(self.setup_gl_context)
            Mesh(
                vertices = vertices,
                indices= indices,
                fmt=self.attr_layout,
                mode='triangles',
                )
            self.cb = Callback(self.reset_gl_context)
        self.vertexes_list.clear()
