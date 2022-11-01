from dataclasses import dataclass
from typing import Any, List
import flet
from flet import Page, Stack, Row, Column,UserControl,Container,Text,Divider, View, ListView,ElevatedButton,ListTile,Icon
from flet import alignment,colors, border_radius, ContainerTapEvent,icons
from graph import ChemQuery
from chempy import Substance, Reaction

@dataclass    
class ElementModel:
    element : Any
    substances: List[Substance]

@dataclass
class SubstanceModel:
    substance : Substance
    reactions : List[Reaction]

class Controller:
    instance = None

    def __init__(self, page):
        self.query = ChemQuery()
        self.views = []
        self.page = page
        # self.data = None
        self._active_view = 0
        self.history = []
        Controller.instance = self

    @property
    def active_view(self):
        return self.views[self._active_view]

    @property
    def active_view_id(self):
        return self._active_view
    
    @active_view_id.setter
    def active_view_id(self,newVal):
        
        view = self.views[self._active_view] 
        view.visible = False
        view.update()
        view = self.views[newVal]
        view.visible = True
        view.update()

        self._active_view = newVal

    def history_push(self):
        self.history.append( (self._active_view, self.active_view.data ))

    def history_pop(self):
        if self.history:
            v, data = self.history[-1]
            self.history = self.history[::-1]  # pop
            self.active_view_id = v
            self.views[v].data = data
            # self.views[self._active_view].update()
            self.page.update()

    def show_element(self, data):
        self.history_push()
        detail = self.query.element_detail(data['id'])
        data = ElementModel(**detail)

        self.views[1].data = data
        self.active_view_id = 1
        self.page.update()

    def show_substance(self,subst):
        self.history_push()
        data = SubstanceModel(substance=subst, reactions=self.query.reactions_of_subst(subst.name))

        # print( self.data.reactions )
        self.views[2].data = data
        self.active_view_id = 2
        self.page.update()

    @staticmethod
    def main(page: Page):

        page.title = "GridView Example"
        # page.theme_mode = "dark"
        page.padding = 50
        # page.horizontal_alignment = "stretch"
        # page.vertical_alignment = "stretch"
        page.update()
        
        instance = Controller(page)
        
        instance.views = [
            ElementChartApp(),
            ElementView(),
            SubstanceView(),
        ]

        page.add( Stack(instance.views,expand=True ), 
            Row([Container(Text("Footer"), bgcolor="yellow", padding=5, expand=True)]))
        page.update()        


class ElementChartApp(UserControl):
    def gen_element_table(self):
        def gen_items(idx, v):
            items = []
            for _idx,x in enumerate(v):
                for n in range(x):
                    if _idx % 2:
                        items.append((0,'-'))
                    else:
                        items.append((idx, Controller.instance.query.element_detail(idx)['element']))
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
            Controller.instance.show_element( e.control.data )

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
            Controller.instance.history_pop()


        return Column([
            Row( [ElevatedButton(text="Back", on_click=on_back_click),
                self.title]),
            Divider(height=9, thickness=3),
            self.lv_subst
        ])

    def update(self):
        def on_subst_click(e):
            Controller.instance.show_substance( e.control.data )
        if type(self.data) is ElementModel:
            self.title.value = self.data.element['name']
            controls = []
            for subst in self.data.substances:
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
        self.reactions_l = ListView(expand=True, spacing=10)
        self.reactions_r = ListView(expand=True, spacing=10)
        def on_back_click(e):
            Controller.instance.history_pop()
        return Column([
            Row( [ElevatedButton(text="Back", on_click=on_back_click),
                self.title]),
            Divider(height=9, thickness=3),
            Row( [self.reactions_l, self.reactions_r]),
        ])

    def update(self):
        if type(self.data) is SubstanceModel:
            self.title.value = self.data.substance.unicode_name
            self.reactions_l.controls.clear()
            for reac in self.data.reactions['left']:
                title = reac.data['unicode']
                content = ListTile(
                            leading=Icon(icons.ALBUM),
                            title=Text(reac.name),
                            subtitle=Text(
                               title
                            ),
                        )
                self.reactions_l.controls.append(content)
            self.reactions_r.controls.clear()
            for reac in self.data.reactions['right']:
                title = reac.data['unicode']
                content = ListTile(
                            leading=Icon(icons.ALBUM),
                            title=Text(reac.name),
                            subtitle=Text(
                               title
                            ),
                        )
                self.reactions_r.controls.append(content)

        super().update()



flet.app(target=Controller.main)