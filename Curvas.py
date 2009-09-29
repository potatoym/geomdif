# -*- coding: utf-8 -*-
from math import *

from PyQt4 import QtCore, QtGui
from pivy.coin import *
from pivy.gui.soqt import *
from superficie.VariousObjects import Bundle2, Bundle
from superficie.VariousObjects import Line, GraphicObject, Curve3D, Sphere, Arrow
from superficie.base import Chapter
from superficie.base import Page
from superficie.util import Vec3
from superficie.util import intervalPartition
from superficie.util import connect, connectPartial
from superficie.Animation import Animation
from superficie.gui import onOff, CheckBox, Slider, Button, VisibleCheckBox, SpinBox
from superficie.gui import DoubleSpinBox
from superficie.Plot3D import ParametricPlot3D

## ---------------------------------- CILINDRO ----------------------------------- ##

def cilindro(col, length):
    sep = SoSeparator()

    cyl = SoCylinder()
    cyl.radius.setValue(0.98)
    cyl.height.setValue(length)
    cyl.parts = SoCylinder.SIDES

    light = SoShapeHints()
#    light.VertexOrdering = SoShapeHints.COUNTERCLOCKWISE
#    light.ShapeType = SoShapeHints.UNKNOWN_SHAPE_TYPE
#    light.FaceType  = SoShapeHints.UNKNOWN_FACE_TYPE

    mat = SoMaterial()
    mat.emissiveColor = col
    mat.diffuseColor = col
    mat.transparency.setValue(0.5)

    rot = SoRotationXYZ()
    rot.axis = SoRotationXYZ.X
    rot.angle = pi / 2

    trans = SoTransparencyType()
#    trans.value = SoTransparencyType.DELAYED_BLEND
    trans.value = SoTransparencyType.SORTED_OBJECT_BLEND
#    trans.value = SoTransparencyType.SORTED_OBJECT_SORTED_TRIANGLE_BLEND

    sep.addChild(light)
    sep.addChild(rot)
    sep.addChild(trans)
    sep.addChild(mat)
    sep.addChild(cyl)

    return sep

## ---------------------------------- ESFERA--------------------------------- ##

def esfera(col):
    sep = SoSeparator()

    comp = SoComplexity()
    comp.value.setValue(1)
    comp.textureQuality.setValue(0.9)

    esf = SoSphere()
    esf.radius = 2.97

    light = SoShapeHints()
    light.VertexOrdering = SoShapeHints.COUNTERCLOCKWISE
    light.ShapeType = SoShapeHints.UNKNOWN_SHAPE_TYPE
    light.FaceType  = SoShapeHints.UNKNOWN_FACE_TYPE

    mat = SoMaterial()
    mat.emissiveColor = col
    mat.diffuseColor = col
    mat.transparency.setValue(0.4)

    trans = SoTransparencyType()
#    trans.value = SoTransparencyType.SORTED_OBJECT_BLEND
    trans.value = SoTransparencyType.SORTED_OBJECT_SORTED_TRIANGLE_BLEND
#    trans.value = SoTransparencyType.DELAYED_BLEND

    sep.addChild(comp)
    sep.addChild(light)
    sep.addChild(trans)
    sep.addChild(mat)
    sep.addChild(esf)

    return sep
## ------------------------------- HELICE CIRCULAR ------------------------------- ##


# 1 implica primer derivada, 2 implica segunda derivada
def param1hc(t):
    return Vec3(cos(t), sin(t), t)
def param2hc(t):
    return Vec3(-sin(t), cos(t), 1)
def param3hc(t):
    return Vec3(-cos(t), -sin(t), 0)



class HeliceCircular(Page):
    def __init__(self):
        Page.__init__(self, u"Hélice Circular")
        tmin = -2 * pi
        tmax = 2 * pi
        npuntos = 200
        self.addChild(cilindro((185. / 255, 46. / 255, 61. / 255), tmax - tmin))
        ## ============================================
        puntos = [[cos(t), sin(t), t] for t in intervalPartition((tmin, tmax, npuntos))]
        curva = Line(puntos,(1, 1, 1), 2,parent=self, nvertices=1)
        bpuntos = 100
        bundle = Bundle(param1hc, param2hc, (tmin, tmax, bpuntos), (116. / 255, 0, 63. / 255), 1.5,visible=True,parent=self)
        bundle.hideAllArrows()
        bundle2 = Bundle(param1hc, param3hc, (tmin, tmax, bpuntos), (116. / 255, 0, 63. / 255), 1.5,visible=True,parent=self)
        bundle2.hideAllArrows()

        self.setupAnimations([curva,bundle,bundle2])



## ------------------------------- HELICE REFLEJADA ------------------------------- ##

class HeliceReflejada(Page):
    def __init__(self):
        Page.__init__(self, u"Hélice Reflejada")
        tmin,tmax,npuntos = (-2 * pi,2 * pi,200)
        self.addChild(cilindro((7. / 255, 83. / 255, 150. / 255), tmax - tmin))
        
        puntos = [[cos(t), sin(t), t] for t in intervalPartition((tmin, tmax, npuntos))]
        puntitos = [[cos(t), sin(t), -t] for t in intervalPartition((tmin, tmax, npuntos))]
        l1 = Line(puntos, (1, 1, 1), 2,parent=self, nvertices=1)
        l2 = Line(puntitos, (128. / 255, 0, 64. / 255), 2,parent=self, nvertices=1)

        bpuntos = 100
        bundle  = Bundle(param1hc, param2hc, (tmin, tmax, bpuntos), (116. / 255, 0, 63. / 255), 1.5,visible=True,parent=self)
        bundle2 = Bundle(param1hc, param3hc, (tmin, tmax, bpuntos), (116. / 255, 0, 63. / 255), 1.5,visible=True,parent=self)
        bundle.hideAllArrows()
        bundle2.hideAllArrows()

        self.setupAnimations([l1,l2,bundle,bundle2])



## -------------------------------LOXODROMA------------------------------- ##


# La rotacion para poder pintar los meridianos
def rot(ang):
    rot = SoRotationXYZ()
    rot.axis = SoRotationXYZ.Z
    rot.angle = ang

    return rot

# Dibuja la loxodroma y la esfera

class Loxi(Page):
    def __init__(self, parent=None):
        Page.__init__(self, "Loxodroma")
        self.creaLoxodroma()

    def creaLoxodroma(self):
        tmin = -50 * pi
        tmax = 50 * pi
        pmin = 0
        pmax = 2 * pi
        r = 3
        m = tan(pi / 60)
        t0 = pi / 2

        puntos2 = [[r * cos(t) / cosh(m * (t-t0)), r * sin(t) / cosh(m * (t-t0)), r * tanh(m * (t-t0))] for t in intervalPartition((tmin, tmax, 2000))]
        puntitos2 = [[0, r * cos(t), r * sin(t)] for t in intervalPartition((pmin, pmax, 200))]

        sep = SoSeparator()
        lox = Line(puntos2, (1, 1, 0), 3,nvertices=1)
        sep.addChild(lox)
        self.setupAnimations([lox])
        sep.addChild(esfera((28. / 255, 119. / 255, 68. / 255)))
        mer = Line(puntitos2, (72. / 255, 131. / 255, 14. / 255))
        for i in range(24):
            sep.addChild(rot(2 * pi / 24))
            sep.addChild(mer)
        self.addChild(sep)

## ------------------------------------------------------------------------ ##

class Alabeada(Page):
    def __init__(self):
        Page.__init__(self, "Alabeada")
        self.setupPlanes()
        ## ============================
        c   = lambda t: Vec3(t,t**2,t**3)
        cp  = lambda t: Vec3(1,2*t,3*t**2)
        cpp = lambda t: Vec3(0,2,6*t)
        ## ============================
        tmin,tmax,npuntos = (-1,1,50)
        altura = -1
        ## ============================
        curva = Curve3D((tmin,tmax,npuntos),lambda t:(t,t**2,t**3), width=3,nvertices=1,parent=self)
        lyz = curva.project(x=altura, color=(0,1,1), width=3, nvertices=1)
        lxz = curva.project(y=altura, color=(1,0,1), width=3, nvertices=1)
        lxy = curva.project(z=altura, color=(1,1,0), width=3, nvertices=1)

        tang = Bundle2(curva, cp,  col=(1,.5,.5), factor=.6, parent=self,visible=True)
        tang.hideAllArrows()
        cot  = Bundle2(curva, cpp, col=(1,.5,.5), factor=.2, parent=self, visible=True)
        cot.hideAllArrows()

        ## ============================
        curvas = [curva, lyz, lxz, lxy]
        ## ============================
        self.setupAnimations(curvas + [tang,cot])

        t1 = Arrow(curva[0],lyz[0],escala=.005,escalaVertice=2,extremos=True,parent=self,visible=False)
    
        connect(self.animations[1],"stateChanged(QTimeLine::State)", lambda state: t1.show() if state==2 else None)
        connect(self.animations[3],"stateChanged(QTimeLine::State)", lambda state: t1.hide() if state==0 else None)

        def trazaCurva(curva2,frame):
            p2 = curva2[frame-1]
            p1 = curva[frame-1]
            t1.setPoints(p1,p2)
            t1.setLengthFactor(.98)

        for i in range(1,4):
            connectPartial(self.animations[i], "frameChanged(int)", trazaCurva, curvas[i])


#        VisibleCheckBox("1a derivada",tang,False,parent=self)
#        VisibleCheckBox("2a derivada",cot, False,parent=self)
        ## ============================
#        Slider(
#            rangep=('w', .2, .6, .6,  20),
#            func=lambda t:(tang.setLengthFactor(t) or cot.setLengthFactor(t)),
#            parent=self
#        )


## -------------------------------TORO------------------------------- ##


class Toro(Page):
    def __init__(self):
        ""
        Page.__init__(self, u"Toro")
        tmin,tmax,npuntos = (0,10*pi,500)

        a = 1
        b = 0.5
        c = .51
        def toroParam1(u,v):
            return ((a+b*cos(v))*cos(u),(a+b*cos(v))*sin(u),b*sin(v))
        def toroParam2(u,v):
            return ((a+c*cos(v))*cos(u),(a+c*cos(v))*sin(u),c*sin(v))
        def curvaPlana(t):
            return (t,t)
        def curvaToro(t):
            return toroParam2(*curvaPlana(t))

        toro = ParametricPlot3D(toroParam1,(0,2*pi),(0,2*pi))
        toro.setTransparencyType(SoTransparencyType.SORTED_OBJECT_SORTED_TRIANGLE_BLEND)
        toro.setTransparency(.4)

        curva = Curve3D((tmin,tmax,npuntos), curvaToro, color=(146./255, 33./255, 86/255.), width=3,nvertices=1,parent=self)


        def recalculaCurva(**kargs):
            "a: vueltas horizontales, b: vueltas verticales"
            keys = kargs.keys()
            if "a" in keys:
                recalculaCurva.a = kargs["a"]
            if "b" in keys:
                recalculaCurva.b = kargs["b"]

            def curvaPlana(t):
                return (recalculaCurva.a*t,recalculaCurva.b*t)
            def curvaToro(t):
                return toroParam2(*curvaPlana(t))
            
            curva.updatePoints(curvaToro)

#        self.animation2 = Animation(recalculaCurva2,(10000,1,20))
#        Button("Curvas2", self.animation2.start, parent=self)

        recalculaCurva.a = 1
        recalculaCurva.b = 1

        sp1 = DoubleSpinBox("a", (0,20,1), lambda x: recalculaCurva(a=x), parent=self)
        sp2 = DoubleSpinBox("b", (0,20,1), lambda x: recalculaCurva(b=x), parent=self)
        sp1.setSingleStep(.005)
        sp2.setSingleStep(.005)


        self.addChild(toro)
        curva.animation.setDuration(5000)
        self.setupAnimations([curva])



## ------------------------------------------------------------------------ ##
figuras = [Loxi, HeliceCircular, HeliceReflejada, Alabeada, Toro]


class Curvas(Chapter):
    def __init__(self):
        Chapter.__init__(self,name="Curvas")
        for f in figuras:
            self.addPage(f())

    def chapterSpecificIn(self):
        print "chapterSpecificIn"
#        self.viewer.setTransparencyType(SoGLRenderAction.SORTED_LAYERS_BLEND)

## ------------------------------------------------------------------------ ##




if __name__ == "__main__":
    import sys
    from superficie.Viewer import Viewer
#    app = main(sys.argv)
    app = QtGui.QApplication(sys.argv)
    visor = Viewer()
    visor.setColorLightOn(False)
    visor.setWhiteLightOn(True)
    visor.addChapter(Curvas())
    visor.getChapterObject().chapterSpecificIn()
    ## ============================
    visor.whichPage = 0
    visor.resize(400, 400)
    visor.show()
    visor.chaptersStack.show()
#    SoQt.mainLoop()
    sys.exit(app.exec_())

