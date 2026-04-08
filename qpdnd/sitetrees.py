from sitetree.utils import item
from core.utils.tree import G3Wtree

# Be sure you defined `sitetrees` in your module.
sitetrees = (
  # Define a tree with `tree` function.
  G3Wtree('qpdnd', title='PDND', module='qpdnd', items=[
      # Then define items and their children with `item` function.
      item('PDND (OGC API)', '#', type_header=True),
      item('ANNCSU', '#', icon_css_class='fa fa-globe', children=[
          item('Aggiungi projetto', 'qpdnd-anncsu-project-add', url_as_pattern=True, icon_css_class='fa fa-plus',
               access_by_perms=['qpdnd.add_anncsuproject']),
          item('Lista projetti', 'qpdnd-anncsu-project-list', url_as_pattern=True, icon_css_class='fa fa-list'),
          item('Agg. Progetto {{ object.project }}', 'qpdnd-anncsu-project-update object.pk', url_as_pattern=True,
               icon_css_class='fa fa-edit', in_menu=False, alias='qpdnd-anncsu-project-update'),
      ]),
  ]),

  G3Wtree('qpdnd_en', title='PDND', module='qpdnd', items=[
      # Then define items and their children with `item` function.
      item('PDND (OGC API)', '#', type_header=True),
      item('ANNCSU', '#', icon_css_class='fa fa-globe', children=[
          item('Add project', 'qpdnd-anncsu-project-add', url_as_pattern=True, icon_css_class='fa fa-plus',
               access_by_perms=['qpdnd.add_anncsuproject']),
          item('Projects list', 'qpdnd-anncsu-project-list', url_as_pattern=True, icon_css_class='fa fa-list'),
          item('Update Progetto {{ object.project }}', 'qpdnd-anncsu-project-update object.pk', url_as_pattern=True,
               icon_css_class='fa fa-edit', in_menu=False, alias='qpdnd-anncsu-project-update'),
      ]),
  ]),
)