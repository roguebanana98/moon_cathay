"""Complete missing channels for standalone Blender previews, not game exports."""
def complete_preview_channels(action,rig):
    slot=action.slots[0];bag=action.layers[0].strips[0].channelbag(slot,ensure=True);curves=bag.fcurves
    existing={(f.data_path,f.array_index) for f in curves};added=0
    for bone in rig.pose.bones:
        for property_name,values in [('location',(0,0,0)),('rotation_quaternion',(1,0,0,0))]:
            path=f'pose.bones["{bone.name}"].{property_name}'
            for axis,value in enumerate(values):
                if (path,axis) in existing:continue
                curve=curves.new(path,index=axis);point=curve.keyframe_points.insert(0,value,options={'FAST'});point.interpolation='CONSTANT';added+=1
    action['preview_identity_channel_count']=added
    return added
