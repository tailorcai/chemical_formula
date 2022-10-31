from turtle import onclick
import flet
from flet import Page, Stack, Row, Column,UserControl,Container,Text,Divider, View, ListView,ElevatedButton,ListTile,Icon
from flet import alignment,colors, border_radius, ContainerTapEvent,icons
from graph import ChemQuery

    
class ElementModel:
    def __init__(self):
        self.element = None
        self.substances = None

class SubstanceModel:
    def __init__(self):
        self.substance = None
        self.reactions = []

class Controller:
    def __init__(self):
        self.query = ChemQuery()
        self.views = []
        self.root_view = None
        self.data = None
        self._active_view = None
        self.history = []

    @property
    def active_view(self):
        return self._active_view
    
    @active_view.setter
    def active_view(self,newVal):
        
        view = self.views[self._active_view] 
        view.visible = False
        view.update()
        view = self.views[newVal]
        view.visible = True
        view.update()

        self._active_view = newVal

    def history_push(self):
        self.history.append( (self._active_view, self.data ))

    def history_pop(self):
        if self.history:
            v, self.data = self.history[-1]
            self.history = self.history[::-1]  # pop
            self.active_view = v
            # self.views[self._active_view].update()
            self.root_view.update()

    def show_element(self, data):
        self.history_push()
        detail = self.query.element_detail(data['id'])
        self.data = ElementModel()
        self.data.element = detail['element']
        self.data.substances = detail['substances']
        self.active_view = 1
        self.root_view.update()

    def show_substance(self,subst):
        self.history_push()
        self.data = SubstanceModel()
        self.data.substance = subst
        self.data.reactions = self.query.reactions_of_subst(subst.name)
        # print( self.data.reactions )
        self.active_view = 2
        self.root_view.update()
        
_controller = Controller()

class ElementChartApp(UserControl):
    def gen_element_table(self):
        def gen_items(idx, v):
            items = []
            for _idx,x in enumerate(v):
                for n in range(x):
                    if _idx % 2:
                        items.append((0,'-'))
                    else:
                        items.append((idx, _controller.query.element_detail(idx)['element']))
                        idx += 1
            return idx, items
        element_table = []
        idx = 1
        for v in ((1,16,1),(2,10,6),(2,10,6),(18,),(18,),(18,)):
            idx, columns = gen_items(idx, v)
            element_table.append( columns )
        return element_table    

    def build(self):
        self.table = self.gen_element_table()

        def element_click(e: ContainerTapEvent):
            _controller.show_element( e.control.data )
            _controller.active_view = 1

        def rows():
            items = []
            for v in self.table:
                def ele_val(item):
                    return item[1]['name'] if item[0] > 0 else '-' 
                r = [Container(
                            content=Text(value=ele_val(item),size=20),
                            data=item[1],
                            alignment=alignment.center,
                            width=50,
                            height=50,
                            bgcolor=colors.BLUE,
                            on_click=element_click
                            # border_radius=border_radius.all(5),
                        ) for item in v]
                row = Row(spacing=0, controls=r)
                items.append(row)
            return items
        return Column(spacing=0, controls=rows())

class ElementView(UserControl):
    def build(self):
        self.visible = False
        self.title = Text("Size 10", size=50)
        self.lv_subst = ListView(spacing=10,expand=True)
        def on_back_click(e):
            _controller.history_pop()


        return Column([
            Row( [ElevatedButton(text="Back", on_click=on_back_click),
                self.title]),
            Divider(height=9, thickness=3),
            self.lv_subst
        ])

    def update(self):
        def on_subst_click(e):
            _controller.show_substance( e.control.data )
        # print( _controller.data.element )
        if type(_controller.data) is ElementModel:
            self.title.value = _controller.data.element['name']
            controls = []
            for subst in _controller.data.substances:
                controls.append( Container(
                        content=Text( value=subst.unicode_name,  ),
                        on_click=on_subst_click,
                        data=subst,))
            self.lv_subst.controls = controls
        super().update()

class SubstanceView(UserControl):
    def build(self):
        self.visible = False
        self.title = Text("Size 10", size=50)
        self.reactions = ListView(expand=True, spacing=10)
        def on_back_click(e):
            _controller.history_pop()
        return Column([
            Row( [ElevatedButton(text="Back", on_click=on_back_click),
                self.title]),
            Divider(height=9, thickness=3),
            self.reactions
        ])

    def update(self):
        if type(_controller.data) is SubstanceModel:
            self.title.value = _controller.data.substance.unicode_name
            self.reactions.controls.clear()
            for reac in _controller.data.reactions['left']:
                title = reac.data['unicode']
                content = ListTile(
                            leading=Icon(icons.ALBUM),
                            title=Text(reac.name),
                            subtitle=Text(
                               title
                            ),
                        )
                self.reactions.controls.append(content)
        super().update()

def main(page: Page):
    page.title = "GridView Example"
    # page.theme_mode = "dark"
    page.padding = 50
    # page.horizontal_alignment = "stretch"
    # page.vertical_alignment = "stretch"
    page.update()
    
    _controller.views = [
        ElementChartApp(),
        ElementView(),
        SubstanceView(),
    ]
    _controller._active_view = 0
    _controller.root_view = page
    page.add( Stack(_controller.views,expand=True ), 
        Row([Container(Text("Footer"), bgcolor="yellow", padding=5, expand=True)]))
    page.update()

flet.app(target=main)