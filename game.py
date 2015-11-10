import simplegui
import math
import random

#in: list of points

#mutates points_list
#trims polygon to be in rectangle defined by xMin, xMax yMin, yMax
def polyTrim(points_list, xMin, xMax, yMin, yMax):
    
    def trimZero(points, axis, axis_n):
        
 
        def backface(x1,y1,x2,y2,x3,y3):
            return ((x3 - x1) * (y2 - y3)) > ((y3 - y1) * (x2 - x3))
                    
        #point on line from point_a to point_b where axis = 0
        def intersection(point_a, point_b, axis, axis_n):
            new_point = []
            for i in range(0,axis_n):
                new_point.append(0)
            if axis_n == 3:
                new_point[axis-2] = (max(point_a[axis-2],point_b[axis-2])-min(point_b[axis-2],point_a[axis-2]))*(max(point_b[axis],point_a[axis])/( abs(point_b[axis])+abs(point_a[axis])))+min(point_b[axis-2],point_a[axis-2])
                new_point[axis-1] = (max(point_a[axis-1],point_b[axis-1])-min(point_b[axis-1],point_a[axis-1]))*(max(point_b[axis],point_a[axis])/( abs(point_b[axis])+abs(point_a[axis])))+min(point_b[axis-1],point_a[axis-1])
                new_point[axis] = 0
            if axis_n == 2:
                new_point[axis] = 0
                new_point[axis-1] = (-(point_b[axis-1]-point_a[axis-1])/(point_b[axis]-point_a[axis]))*point_a[axis]  + point_a[axis-1]
            return new_point
        
        backface_start = backface(points[0][0],points[0][1],points[1][0],points[1][1],points[2][0],points[2][1])

        min = 1000000000000
        max = -1000000000000
        for point in points:
            if point[axis] < min:
                min = point[axis]
            if point[axis] > max:
                max = point[axis]
                
        if min < 0 and max > 0:
            i = 0
            while points[i][axis] <= 0:
                i = (i+1)%len(points)
            while points[i][axis] >= 0:
                i = (i+1)%len(points)

            point_a = intersection(points[i],points[i-1],axis,axis_n)
            cut_start = i
            while points[i][axis] < 0:
                i = (i+1)%len(points)
            point_b = intersection(points[i],points[i-1],axis,axis_n)
            cut_end = i

            if cut_start > cut_end:
                for  i in range(cut_start,len(points)):
                    points.pop(cut_start)
                for  i in range(0,cut_end):
                    points.pop(0)
            else:
                for i in range(cut_start,cut_end):
                    points.pop(cut_start)
                
            backface_end = backface(points[0][0],points[0][1],point_a[0],point_a[1],point_b[0],point_b[1])
        
            if backface_start == backface_end:
                points.insert(cut_start,point_b)
                points.insert(cut_start,point_a)
            else:
                points.insert(cut_start,point_a)
                points.insert(cut_start,point_b)
    
    #can optimize by not running for edges of screen
    def trimAxis(points, min, max, axis, axis_n):
        if min != 0:
            for point in points:
                point[axis] -= min
        trimZero(points, axis, axis_n)
        for point in points:
            point[axis] = -(point[axis] + min - max)
        trimZero(points, axis, axis_n)
        for point in points:
            point[axis] = -point[axis] + max
            
    trimAxis(points_list, xMin, xMax, 0, 2)
    trimAxis(points_list, yMin, yMax, 1, 2)

        
    

class DrawEngine:
          
    class Camera:
        def draw(self, canvas):
            list = []
            for a in world_objects:
                b = a.transform(self)
                if b is not None:
                    list.append(b)
            list.sort()
            for twoDPoly in list:
                twoDPoly.draw(canvas, self)
                
        def __init__(self, x, y, z, x_shift, y_shift, xAngle, yAngle, zAngle, world_objects, screen_x, screen_y, screen_width, screen_height):
            self.x = x
            self.y = y
            self.z = z
            self.x_shift = x_shift
            self.y_shift = y_shift
            self.y_rotate = yAngle
            self.world_objects = world_objects
            self.screen_x = screen_x
            self.screen_y = screen_y
            self.screen_width = screen_width
            self.screen_height = screen_height
            self.focalLength = 250.0
            self.vanishingPointX, self.vanishingPointY = screen_width/2.0, screen_height/2.0
            
        def move(self, x_change, y_change, z_change):                                                                                                        #WHY????
            self.x += x_change
            self.y += y_change
            self.z += z_change
            
        def turn(self, y_change):
            self.y_rotate += y_change
    
    class WorldPoint:
        def __init__(self,x,y,z):
            self.x = x
            self.y = y
            self.z = z
            
        def __getitem__(self,key):
            if key == 0:
                return self.x
            if key == 1:
                return self.y
            if key == 2:
                return self.z

        def transform(self,camera):
            x = self.x + camera.x
            y = self.y + camera.y 
            z = self.z + camera.z
            
            cos_y = math.cos(camera.y_rotate)
            sin_y = math.sin(camera.y_rotate)
            
            old_x = x
            x = x * cos_y - (z+camera.focalLength)*sin_y
            z = (z+camera.focalLength) * cos_y + old_x * sin_y - camera.focalLength
            
            if camera.focalLength + z == 0:
                scale = 1000000000000
            else:
                scale = camera.focalLength/(camera.focalLength + z)

            return DrawEngine.ScreenPoint(
                camera.vanishingPointX + x * abs(scale), 
                camera.vanishingPointY + y * abs(scale), scale)
    
    class ScreenPoint:
        def __init__(self,x,y,scale):
            self.x = x
            self.y = y
            self.scale = scale

        def __getitem__(self,key):
            if key == 0:
                return self.x
            if key == 1:
                return self.y
            if key == 2:
                return self.scale
            
    class ScreenPoly:
        def __init__(self, points, color_r, color_g, color_b):
            self.color_r = color_r
            self.color_g = color_g
            self.color_b = color_b
            
            self.points = points
            self.priority = 0
            for point in self.points:
                self.priority += point[2]
            self.priority /= len(self.points)
        
        def __getitem__(self,key):
            return list[key]
        
        def __cmp__(self, other):
            if self.priority < other.priority:
                return -1
            elif self.priority == other.priority:
                return 0
            return 1
            
        def draw(self, canvas, camera):
            new = []
            for point in self.points:
                new.append([point[0]+camera.x_shift, point[1]+camera.y_shift])
            minX =  10000000000
            maxX = -10000000000
            minY = 1000000000
            maxY = -10000000000
            for point in new:
                if point[0] < minX:
                    minX = point[0]
                if point[1] < minY:
                    minY = point[1]
                if point[0] > maxX:
                    maxX = point[0]
                if point[1] > maxY:
                    maxY = point[1]
            if maxX > camera.screen_x and minX < camera.screen_x+camera.screen_width and maxY > camera.screen_y and minY < camera.screen_y+camera.screen_height:
                polyTrim(new, camera.screen_x, camera.screen_x+camera.screen_width, camera.screen_y, camera.screen_y+camera.screen_height)
                canvas.draw_polygon(new, 1, 'rgb(0,0,255)',"rgb("+str(self.color_r)+","+str(self.color_g)+","+str(self.color_b)+")")

    class WorldPoly:
        def __init__(self,points, color_r = random.randrange(70,100), color_g = random.randrange(200,255),color_b = random.randrange(70,100)):
            self.points = points
            
            self.color_r = color_r
            self.color_g = color_g
            self.color_b = color_b

        def transform(self, camera):
            line_thinkness = 1
            points = []
            maxZ = -1000000000
            minZ = 10000000000
            for point in self.points:
                points.append( point.transform(camera) )
                if points[len(points)-1][2] > maxZ:
                    maxZ = points[len(points)-1][2]
                if points[len(points)-1][2] < maxZ:
                    minZ = points[len(points)-1][2]

            if maxZ > 0:
                if minZ < 0:
                    x1 = points[0][0]
                    y1 = points[0][1]
                    z1 = points[0][2] #NO
                    x2 = points[1][0]
                    y2 = points[1][1]
                    z2 = points[1][2]
                    x3 = points[2][0]
                    y3 = points[2][1]
                    z3 = points[2][2] #CRASHES LESS THEN THREE
                   
                    #this is really wrong 
                    def backface(x1,y1,z1,x2,y2,z2,x3,y3,z3):
                        return ((x3 - x1) * (y2 - y3)) > ((y3 - y1) * (x2 - x3))
                    
                    backface_start = backface(x1,y1,z1,x2,y2,z2,x3,y3,z3)
        
                    i = 0
                    while points[i][2] < 0:
                        i = (i+1)%len(points)
                        
                    while points[i][2] > 0:
                        i = (i+1)%len(points)
                    point_a = ( ((max(points[i-1][0],points[i][0])-min(points[i][0],points[i-1][0]))*(max(points[i][2],points[i-1][2])/( abs(points[i][2])+abs(points[i-1][2])))+min(points[i][0],points[i-1][0])),
                               ((max(points[i-1][1],points[i][1])-min(points[i][1],points[i-1][1]))*(max(points[i][2],points[i-1][2])/( abs(points[i][2])+abs(points[i-1][2])))+min(points[i][1],points[i-1][1])),0) 
                    cut_start = i
                    while points[i][2] < 0:
                        i = (i+1)%len(points)
                    point_b = ( ((max(points[i-1][0],points[i][0])-min(points[i][0],points[i-1][0]))*(max(points[i][2],points[i-1][2])/( abs(points[i][2])+abs(points[i-1][2])))+min(points[i][0],points[i-1][0])),
                               ((max(points[i-1][1],points[i][1])-min(points[i][1],points[i-1][1]))*(max(points[i][2],points[i-1][2])/( abs(points[i][2])+abs(points[i-1][2])))+min(points[i][1],points[i-1][1])),0)
                    cut_end = i
                    if cut_start > cut_end:
                        for  i in range(cut_start,len(points)):
                            points.pop(cut_start)
                        for  i in range(0,cut_end):
                            points.pop(0)
                            
                        backface_end = backface(x1,y1,z1,point_a[0],point_a[1],point_a[2],point_b[0],point_b[1],point_b[2])
        
                        if backface_start != backface_end:
                            points.insert(cut_start,point_a)
                            points.insert(cut_start,point_b)
                        else:
                            points.insert(cut_start,point_b)
                            points.insert(cut_start,point_a)
                    else:
                        for  i in range(cut_start,cut_end):
                            points.pop(cut_start)
                        points.insert(cut_start,point_b)
                        points.insert(cut_start,point_a)
                return DrawEngine.ScreenPoly(points, self.color_r, self.color_g, self.color_b)
            return None

world_objects = []
n = 12
l = 300 

for y in range(0,n):
    for x in range(0,n):
        if random.random() > 0.75:
            world_objects.append(DrawEngine.WorldPoly([DrawEngine.WorldPoint(l+x*l, 0, l+y*l),
                                                      DrawEngine.WorldPoint(0+x*l, 0, l+y*l),
                                                      DrawEngine.WorldPoint(0+x*l, 0, 0+y*l), 
                                                      DrawEngine.WorldPoint(l+x*l, 0, 0+y*l)]))
WIDTH = 1600
HEIGHT = 800


left_camera = DrawEngine.Camera(0,0,0, 0,       0, 0,0,0, world_objects, 0,       0, WIDTH/2, HEIGHT)
right_camera = DrawEngine.Camera(0,0,0, WIDTH/2,0, 0,0,0, world_objects ,WIDTH/2 ,0, WIDTH/2, HEIGHT)

def render_field(canvas):
    right_camera.draw(canvas)
    left_camera.draw(canvas)
    canvas.draw_line((WIDTH/2, 0), (WIDTH/2, HEIGHT), 4, 'White')
        
#####################################################################
#### Key handler stuff for testing
    
keys_down = {
    simplegui.KEY_MAP['up']: False,
    simplegui.KEY_MAP['down']: False,
    simplegui.KEY_MAP['left']: False,
    simplegui.KEY_MAP['right']: False,
    simplegui.KEY_MAP['o']: False,
    simplegui.KEY_MAP['p']: False,
    simplegui.KEY_MAP['w']: False,
    simplegui.KEY_MAP['a']: False,
    simplegui.KEY_MAP['s']: False,
    simplegui.KEY_MAP['d']: False,
    simplegui.KEY_MAP['q']: False,
    simplegui.KEY_MAP['e']: False
}
    
def set_keydown_handler(k):
    global keys_down
    keys_down[k] = True
    
def set_keyup_handler(k):
    global keys_down
    keys_down[k] = False
            
def key_action():
    global draw_engine,keys_down
 
    if keys_down[simplegui.KEY_MAP["up"]]:
        right_camera.move(0,0,-10)
        #left_camera.turn(math.pi * 0.025,0,0)
        #right_camera.turn(0)
    if keys_down[simplegui.KEY_MAP["down"]]:
        right_camera.move(0,0,10)
        #left_camera.turn(math.pi * -0.025,0,0)
        #right_camera.turn(0)
    if keys_down[simplegui.KEY_MAP["left"]]:
        right_camera.move(-10,0,0)
        #left_camera.turn(0,math.pi * -0.025,0)
        #right_camera.turn(math.pi * -0.025)
    if keys_down[simplegui.KEY_MAP["right"]]:
        right_camera.move(10,0,0)
        #left_camera.turn(0,math.pi * 0.025,0)
        #right_camera.turn(math.pi * 0.025)
    if keys_down[simplegui.KEY_MAP["o"]]:
        right_camera.move(0,-10,0)
        #left_camera.turn(0,0,math.pi * 0.025)
        #right_camera.turn(0)
    if keys_down[simplegui.KEY_MAP["p"]]:
        right_camera.move(0,10,0)
        #left_camera.turn(0,0,math.pi * -0.025)
        #right_camera.turn(0)
        
    if keys_down[simplegui.KEY_MAP["w"]]:
        left_camera.move(0,0,-10)
    if keys_down[simplegui.KEY_MAP["a"]]:
        left_camera.move(-10,0,0)
    if keys_down[simplegui.KEY_MAP["s"]]:
        left_camera.move(0,0,10)
    if keys_down[simplegui.KEY_MAP["d"]]:
        left_camera.move(10,0,0)
    if keys_down[simplegui.KEY_MAP["q"]]:
        left_camera.move(0,-10,0)
    if keys_down[simplegui.KEY_MAP["e"]]:
        left_camera.move(0,10,0)

#######################################################################
##### game loop and make frame
    
def game_loop(canvas):
    render_field(canvas)
    key_action()



frame = simplegui.create_frame("", WIDTH, HEIGHT)
frame.set_draw_handler(game_loop)
frame.set_keydown_handler(set_keydown_handler)
frame.set_keyup_handler(set_keyup_handler)

frame.start()
