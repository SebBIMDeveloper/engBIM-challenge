import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')
clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')

from pyrevit import revit, script
import wpf
from System import Windows
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ISelectionFilter, ObjectType
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.Exceptions import OperationCanceledException

# Load XAML UI file
xamlfile = script.get_bundle_file('ui.xaml')

class CategorySelectionFilter(ISelectionFilter):
    """Selection filter to allow only elements of a specific category."""
    def __init__(self, category_name):
        self.category_name = category_name

    def AllowElement(self, elem):
        return elem.Category and elem.Category.Name == self.category_name

    def AllowReference(self, reference, position):
        return False

class MyWindow(Windows.Window):
    def __init__(self):
        wpf.LoadComponent(self, xamlfile)
        self.doc = revit.doc
        self.uidoc = revit.uidoc
        self.selected_elements = []
        self.start_element = None
        self.horizontal_grids = []
        self.vertical_grids = []
        self.populate_ComboBox()
        self.get_grids()

    def populate_ComboBox(self):
        """Fills the ComboBox with visible categories in the active view."""
        active_view = self.doc.ActiveView
        self.categoryComboBox.Items.Clear()
        visible_categories = [
            cat.Name for cat in self.doc.Settings.Categories
            if cat and cat.CategoryType == CategoryType.Model and
            FilteredElementCollector(self.doc, active_view.Id)
            .WherePasses(ElementCategoryFilter(cat.Id))
            .WhereElementIsNotElementType()
            .GetElementCount() > 0
        ]
        for category_name in sorted(visible_categories):
            self.categoryComboBox.Items.Add(category_name)

        self.categoryComboBox.SelectedIndex = 0

    def on_select_elements_click(self, sender, eventArgs):
        """Handles selection of multiple elements in Revit."""
        selected_category = self.categoryComboBox.SelectedItem
        selection_filter = CategorySelectionFilter(selected_category)

        self.Hide()
        try:
            self.selected_elements = self.uidoc.Selection.PickElementsByRectangle(
                selection_filter, "Select elements using a selection rectangle."
            )
        except OperationCanceledException:
            TaskDialog.Show("Selection Canceled", "No elements were selected.")
        finally:
            self.ShowDialog()

    def on_select_start_element_click(self, sender, eventArgs):
        """Handles selection of a reference element."""
        selected_category = self.categoryComboBox.SelectedItem
        selection_filter = CategorySelectionFilter(selected_category)

        self.Hide()
        try:
            start_selection = self.uidoc.Selection.PickObject(
                ObjectType.Element, selection_filter, "Select a reference element."
            )
            self.start_element = self.doc.GetElement(start_selection.ElementId)
        except OperationCanceledException:
            TaskDialog.Show("Selection Canceled", "No reference element was selected.")
        finally:
            self.ShowDialog()

    def get_grids(self):
        """Retrieves all grids in the project and classifies them as horizontal or vertical."""
        grids = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
        for grid in grids:
            curve = grid.Curve
            if curve:
                direction = curve.Direction
                if abs(direction.X) > abs(direction.Y):
                    self.horizontal_grids.append(grid)
                else:
                    self.vertical_grids.append(grid)

    def get_element_midpoint(self, element):
        """Gets the midpoint of an element's location, handling both LocationPoint and LocationCurve."""
        location = element.Location
        if location:
            if hasattr(location, "Point"):  # If it's a LocationPoint
                return location.Point
            elif hasattr(location, "Curve"):  # If it's a LocationCurve (like walls, beams, pipes)
                return location.Curve.Evaluate(0.5, True)  # Midpoint of the curve
        return None  # Return None if no valid location

    def get_nearest_grid_intersection(self, element):
        """Finds the closest grid intersection to the element."""
        element_point = self.get_element_midpoint(element)
        if not element_point:
            return None

        closest_h, closest_v = None, None
        min_h_dist, min_v_dist = float("inf"), float("inf")

        for grid in self.horizontal_grids:
            grid_curve = grid.Curve
            projected_point = grid_curve.Project(element_point).XYZPoint
            distance = element_point.DistanceTo(projected_point)
            if distance < min_h_dist:
                min_h_dist = distance
                closest_h = grid

        for grid in self.vertical_grids:
            grid_curve = grid.Curve
            projected_point = grid_curve.Project(element_point).XYZPoint
            distance = element_point.DistanceTo(projected_point)
            if distance < min_v_dist:
                min_v_dist = distance
                closest_v = grid

        if closest_h and closest_v:
            return "{}-{}".format(closest_v.Name, closest_h.Name)
        return None

    def get_or_create_shared_parameter(self, param_name):
        """Checks if the shared parameter exists, creates it if it does not, and ensures it is assigned to the selected categories."""
        app = self.doc.Application
        shared_param_file = app.OpenSharedParameterFile()

        if not shared_param_file:
            TaskDialog.Show("Error", "No shared parameter file found. Please configure it in Revit.")
            return None

        param_definition = None
        for group in shared_param_file.Groups:
            for definition in group.Definitions:
                if definition.Name == param_name:
                    param_definition = definition
                    break
            if param_definition:
                break

        if not param_definition:
            with Transaction(self.doc, "Create Shared Parameter: {}".format(param_name)) as t:
                t.Start()
                group = shared_param_file.Groups.Create("Shared Parameters") if "Shared Parameters" not in [g.Name for g in shared_param_file.Groups] else shared_param_file.Groups.Item["Shared Parameters"]
                options = ExternalDefinitionCreationOptions(param_name, ParameterType.Text)
                param_definition = group.Definitions.Create(options)
                t.Commit()

        return param_definition

    def bind_shared_parameter_to_categories(self, param_definition, categories):
        """Ensures shared parameters are assigned to the selected categories."""
        if not param_definition:
            return False

        app = self.doc.Application
        param_bindings = self.doc.ParameterBindings

        with Transaction(self.doc, "Bind Shared Parameter: {}".format(param_definition.Name)) as t:
            t.Start()
            category_set = app.Create.NewCategorySet()

            for category in categories:
                if category:
                    try:
                        category_set.Insert(category)
                    except:
                        continue

            if not category_set.IsEmpty:
                binding = app.Create.NewInstanceBinding(category_set)
                if not param_bindings.Contains(param_definition):
                    param_bindings.Insert(param_definition, binding, BuiltInParameterGroup.PG_IDENTITY_DATA)
                else:
                    param_bindings.ReInsert(param_definition, binding, BuiltInParameterGroup.PG_IDENTITY_DATA)

            t.Commit()
            return True

    def on_start_numbering_click(self, sender, eventArgs):
        """Executes numbering and ensures parameters exist."""
        if not self.selected_elements:
            TaskDialog.Show("Error", "No elements were selected for numbering.")
            return
        if not self.start_element:
            TaskDialog.Show("Error", "No start element was selected for numbering.")
            return

        param_names = ["Grid Square", "Number"]
        selected_categories = {el.Category for el in self.selected_elements if el and el.Category}

        for param in param_names:
            shared_param = self.get_or_create_shared_parameter(param)
            if shared_param:
                self.bind_shared_parameter_to_categories(shared_param, selected_categories)

        with Transaction(self.doc, "Number Elements") as t:
            t.Start()
            total_elements = len(self.selected_elements)
            step = 100.0 / total_elements if total_elements else 1

            for i, element in enumerate(self.selected_elements):
                num_param = element.LookupParameter("Number")
                grid_param = element.LookupParameter("Grid Square")
                intersection = self.get_nearest_grid_intersection(element)

                if num_param:
                    num_param.Set(str(i + 1))
                if grid_param and intersection:
                    grid_param.Set(intersection)

                self.progressBar.Value = (i + 1) * step
                self.progressText.Text = "{}%".format(int(self.progressBar.Value))

            t.Commit()

MyWindow().ShowDialog()
