from sitetree.utils import item
from core.utils.tree import G3Wtree

# Be sure you defined `sitetrees` in your module.
sitetrees = (
  # Define a tree with `tree` function.
  G3Wtree('qpdnd', title='PDND', module='qpdnd', items=[
      # Then define items and their children with `item` function.
      item('PDND (OGC API)', '#', type_header=True),
      item('Servizi', '#', icon_css_class='fa fa-globe', children=[
          item('Aggiungi servizio', 'qpdnd-project-add', url_as_pattern=True, icon_css_class='fa fa-plus',
               access_by_perms=['qpdnd.add_qpdndproject']),
          item('Lista servizi', 'qpdnd-project-list', url_as_pattern=True, icon_css_class='fa fa-list'),
          item('Agg. servizio {{ object.title }}', 'qpdnd-project-update object.pk', url_as_pattern=True,
               icon_css_class='fa fa-edit', in_menu=False, alias='qpdndproject-update'),
      ]),
  ]),

  G3Wtree('qpdnd_en', title='PDND', module='qpdnd', items=[
      # Then define items and their children with `item` function.
      item('PDND (OGC API)', '#', type_header=True),
      item('Services', '#', icon_css_class='fa fa-globe', children=[
          item('Add reporting', 'qpdnd-project-add', url_as_pattern=True, icon_css_class='fa fa-plus',
               access_by_perms=['qpdnd.add_qpdndproject']),
          item('Services list', 'qpdnd-project-list', url_as_pattern=True, icon_css_class='fa fa-list'),
          item('Update service {{ object.title }}', 'qpdnd-project-update object.pk', url_as_pattern=True,
               icon_css_class='fa fa-edit', in_menu=False, alias='qpdndproject-update'),
      ]),
  ]),
)