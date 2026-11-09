"""Shared metal/mineral palette; generated shader wear, no image textures."""
MATERIALS={
 'portal-film':('#41c9ed',.3,0,0), 'portal-film-amber':('#d3ac69',.3,0,0),
 'shield-trace':('#65b9df',.3,.1,.65),
 'alloy':('#b6c4c5',.32,.78,0), 'alloy-dark':('#42535a',.42,.82,0),
 'mechanism':('#111d29',.3,.74,0), 'piston':('#8aa5b3',.19,.92,0),
 'patina':('#536b68',.77,.45,0), 'fastener':('#1d3038',.48,.8,0),
 'mineral':('#424c48',.85,.12,0), 'mineral-edge':('#68716b',.71,.22,0),
 'circuit':('#80e1ff',.27,.18,2.1), 'optic':('#defaff',.16,.1,6),
 'radiolaria':('#a5f6ff',.22,.05,3.0), 'temporal':('#67ceff',.2,.15,3.4),
 'vex-patina':('#837757',.48,.7,0), 'vex-polished':('#beb394',.32,.75,0),
}


def add_wear(material,name):
    """Deterministic object-space multiscale mineral deposits, shared per material."""
    if name not in ['alloy','alloy-dark','vex-patina','vex-polished','mineral','mineral-edge']:return
    nodes=material.node_tree.nodes;links=material.node_tree.links;bsdf=nodes['Principled BSDF']
    coordinate=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5.0;noise.inputs['Detail'].default_value=3.0
    links.new(coordinate.outputs['Object'],noise.inputs['Vector'])
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[1].position=.78
    rough=MATERIALS[name][1];ramp.color_ramp.elements[0].color=(max(.1,rough-.13),)*3+(1,);ramp.color_ramp.elements[1].color=(min(.95,rough+.21),)*3+(1,)
    links.new(noise.outputs['Fac'],ramp.inputs['Fac']);links.new(ramp.outputs['Color'],bsdf.inputs['Roughness'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.035
    links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
