"""Check geometric curvature, not browser raster fidelity."""
import json

def curvature(x, n=4):
    y = (1-x**n)**(1/n)
    first = -x**(n-1) * y**(1-n)
    second = -(n-1)*x**(n-2)*y**(1-n) - (n-1)*x**(2*n-2)*y**(1-2*n)
    return abs(second)/(1+first*first)**1.5

samples = [{'x':x, 'curvature':curvature(x)} for x in [0.1,0.01,0.001]]
assert samples[-1]['curvature'] < samples[0]['curvature']
assert curvature(0) == 0
assert 0 != 1/32
print(json.dumps({'model':'x^4+y^4=1, unit axes', 'samples':samples, 'endpoint_curvature':curvature(0), 'radius32_line_curvature':0, 'radius32_arc_curvature':1/32, 'css_raster_verified':False}, indent=2))
