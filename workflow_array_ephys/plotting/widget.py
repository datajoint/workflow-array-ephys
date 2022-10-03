import datajoint as dj
from ipywidgets import widgets as wg
from workflow_array_ephys.pipeline import ephys, report

probe_dropdown = wg.Dropdown(
    options=report.ProbeLevelReport.fetch("KEY", as_dict=True),
    description="Select Probe Insertion : ",
    disabled=False,
    layout=wg.Layout(
        width="100%",
        display="flex",
        flex_flow="row",
        justify_content="space-between",
        grid_area="processed_dropdown",
    ),
    style={"description_width": "150px"},
)


unit_dropdown = wg.Dropdown(
    options=(ephys.CuratedClustering.Unit).fetch("KEY", as_dict=True),
    description="Select Units : ",
    disabled=False,
    layout=wg.Layout(
        width="100%",
        display="flex",
        flex_flow="row",
        justify_content="space-between",
        grid_area="processed_dropdown",
    ),
    style={"description_width": "100px"},
)
