"""Read existing cases and prove that common transfer regressions are rejected."""
import argparse
import json
from pathlib import Path

import cad_checks as checks


def expect_rejected(action):
    try:
        action()
    except (ValueError,KeyError) as error:
        return {'rejected':True,'message':str(error)}
    raise AssertionError('A deliberately invalid in-memory case was accepted')


def validate(spec,root):
    import ezdxf
    result=checks.run_spec(spec,root)
    config=json.loads(Path(spec).read_text(encoding='utf-8'))
    tests={}
    for case in config['cases']:
        source=ezdxf.readfile(root/case['source'])
        before=ezdxf.readfile(root/case['before'])
        altered=ezdxf.readfile(root/case['after'])
        original_hash=checks.digest(root/case['after'])
        kwargs={'exclude':case.get('exclude_source_handles',()),
                'layer_map':case.get('layer_map'),'handle_layer_map':case.get('handle_layer_map')}
        ref,=[e for e in altered.modelspace().query('INSERT') if e.dxf.name==case['block']]
        original_scale=ref.dxf.yscale
        ref.dxf.yscale*=1.01
        scale=expect_rejected(lambda:checks.verify_native(source,altered,case['block'],**kwargs))
        ref.dxf.yscale=original_scale
        block=altered.blocks[case['block']]
        block.delete_entity(next(iter(block)))
        missing=expect_rejected(lambda:checks.verify_native(source,altered,case['block'],**kwargs))
        altered=ezdxf.readfile(root/case['after'])
        old=next(e for e in before.modelspace() if e.dxftype()=='LWPOLYLINE')
        altered.entitydb[old.dxf.handle].dxf.elevation+=.1
        protected=expect_rejected(lambda:checks.retained_objects(before,altered))
        prior_groups=list(before.modelspace().query('INSERT'))
        if prior_groups:
            altered=ezdxf.readfile(root/case['after'])
            block=altered.blocks[prior_groups[0].dxf.name]
            next(iter(block)).dxf.color=242
            prior_block=expect_rejected(lambda:checks.retained_objects(before,altered))
        else:
            prior_block={'not_applicable':'The original target has no prior model INSERT group.'}
        altered=ezdxf.readfile(root/case['after'])
        style=next(iter(before.styles))
        altered.styles.get(style.dxf.name).dxf.font='__read_only_probe__.ttf'
        shared_style=expect_rejected(lambda:checks.retained_objects(before,altered))
        if original_hash!=checks.digest(root/case['after']):
            raise AssertionError('Read-only regression tests changed CAD input')
        tests[case['name']]={'nonuniform_scale':scale,'missing_copy':missing,
                            'protected_evidence_modified':protected,'prior_group_modified':prior_block,
                            'shared_style_modified':shared_style}
    result['in_memory_negative_controls']=tests
    result['all_negative_controls_rejected']=True
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec',type=Path)
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--ezdxf-path',type=Path)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    checks.load_ezdxf(args.ezdxf_path)
    result=validate(args.spec,args.project_root)
    encoded=json.dumps(result,ensure_ascii=False,indent=2)
    if args.report:
        with args.report.open('x',encoding='utf-8') as stream:
            stream.write(encoded+'\n')
    else:
        print(encoded)


if __name__=='__main__':
    main()
