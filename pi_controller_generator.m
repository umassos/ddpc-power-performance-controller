function [Kp, Ki] = PIControllerGenerator(a, b)   
    sys = tf(b, [1, -a], 1)
    [C_pi, info] = pidtune(sys, 'PI')
    [Kp, Ki] = piddata(C_pi)
end
