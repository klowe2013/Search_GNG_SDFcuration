Functional copy of InteractiveSDFs using Flask instead of Dash

This is an interactive plotting of SDFs for the pro/no search task by condition. Partly for increased functionality and partly for self-learning, this version uses basic Flask instead of Dash so that the HTML, vanilla JS, and Python all interact with one another.

This also has increased functionality because clicks can be translated into SST/CDT measurements, which are inferred by the conditions that are visible at a given point of time. This does not update a database with the updated values yet, but next iteration will pickle the dict that contains these values. Future editions will write to database.

To-do:
(1) Add database writing for SST/CDT values
(2) Parse out login page to different landing page
(3) Ultimately, spikes should be used instead of SDFs and another page should handle quality control for spike inclusion