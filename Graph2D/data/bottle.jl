function f(u, v)
    # if v < pi
    #     x = (2.5 - 1.5*cos(v))*cos(u)
    #     y = (2.5 - 1.5*cos(v))*sin(u)
    #     z = -2.5*sin(v)
    # elseif v < 2*pi
    #     x = (2.5 - 1.5*cos(v))*cos(u)
    #     y = (2.5 - 1.5*cos(v))*sin(u)
    #     z = 3*v - 3*pi
    # elseif v < 3*pi
    #     x = -2+(2+cos(u))*cos(v)
    #     y = sin(u)
    #     z = (2+cos(u))*sin(v) + 3*pi
    # else
    #     x = -2 + 2*cos(v) - cos(u)
    #     y = sin(u)
    #     z = -3*v + 12*pi
    # end
    x =u * sin(u) * cos(v)
    y =  u * cos(u) * cos(v)
    z = u * sin(v)
    return x, y, z
end
max_u = 3*pi
max_v = pi
step = 0.1
fd = open("mesh.csv", "w") 
write(fd, "# y z\n")
for u in 0:step:max_u
    for v in 0:step:max_v
        x, y, z = f(u, v)
        write(fd, "$x $y $z\n")
        x, y, z = f(u+step, v)
        write(fd, "$x $y $z\n")
        x, y, z = f(u+step, v+step)
        write(fd, "$x $y $z\n")
        x, y, z = f(u, v+step)
        write(fd, "$x $y $z\n")
    end
    write(fd, "\n")
end
close(fd)
