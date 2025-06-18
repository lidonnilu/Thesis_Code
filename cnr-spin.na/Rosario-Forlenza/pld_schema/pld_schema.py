
import os
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fabrication_facilities.schema_packages.fabrication_utilities import FabricationProcessStep
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import ELNAnnotation
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import Datetime, MEnum, Package, Quantity, Section, SubSection
from plotly.subplots import make_subplots

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

m_package = Package(name='PLD-MODA-LAB Schema')

class RHEEDImage(ArchiveSection):
    """
   Section for inserting RHEED images
    """
    m_def = Section(
        a_eln={
            'hide': ['lab_id', 'name'],
            'properties':{
                'order': [
                    'image_name',
                    'image_description',
                    'image_file'
                ]
            }
        }
    )

    image_name = Quantity(
        type=str,
        description='RHEED image name',
        a_eln={'component': 'StringEditQuantity'}
    )
    
    image_description = Quantity(
        type=str,
        description='RHEED image description',
        a_eln={'component': 'StringEditQuantity'}
    )
    
    image_file = Quantity(
        type=str,
        description='Path or upload RHEED image',
        a_eln={
            'component': 'FileEditQuantity',
            'label': 'Upload Image'
        }
    )


class RHEEDIntensityPlot(PlotSection, EntryData):
    """
    Class to visualize RHEED intensity over time for different diffraction orders.
    Optimized for large datasets (tens of thousands of points).
    """
    m_def = Section()

    data_file = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='FileEditQuantity',
            defaultValue='',
            props=dict(
                fileTypes=['csv', 'txt'],
                placeholder='Upload the CSV file with RHEED data'
            )
        )
    )

    time = Quantity(
        type=float,
        shape=["*"],
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 's'
        },
        unit="s",
        description="Acquisition time",
    )

    intensity_11 = Quantity(
        type=float,
        shape=["*"],
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'J/(cm**2*s)',
            'label': 'Intensity (1,1)'  # <--- Display name in UI
        },
        unit="J/(cm**2*s)",
        description="Intensity of the maximum of order (1,1)",
    )

    intensity_00 = Quantity(
        type=float,
        shape=["*"],
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'J/(cm**2*s)',
            'label': 'Intensity (0,0)'  # <--- Display name in UI
        },
        unit="J/(cm**2*s)",
        description="Intensity of the maximum of order (0,0)",
    )

    intensity_1m1 = Quantity(
        type=float,
        shape=["*"],
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'J/(cm**2*s)',
            'label': 'Intensity (1,-1)'  # <--- Display name in UI
        },
        unit="J/(cm**2*s)",
        description="Intensity of the maximum of order (1,-1)",
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        """
        Optimized method to load and process large datasets from the CSV file.
        """
        MAX_DATA_POINTS = 50000 #Threshold beyond which to perform subsampling
        
        if self.data_file:
            try:
                # Get the absolute path of the file
                
                raw_dir = archive.m_context.raw_path()
                raw_file_path = os.path.join(raw_dir, self.data_file)
                
                df = pd.read_csv(
                    raw_file_path,
                    dtype={
                        'time': float,
                        'intensity_11': float,
                        'intensity_00': float,
                        'intensity_1m1': float
                    },
                    engine='c',
                    memory_map=True
                )
                
                required_columns = ['time', 'intensity_11', 'intensity_00', 'intensity_1m1']
                if not all(col in df.columns for col in required_columns):
                    missing = [col for col in required_columns if col not in df.columns]
                    logger.error(f"Missing columns in the CSV file: {missing}")
                    return

                for col in required_columns:
                    if not pd.to_numeric(df[col], errors='coerce').notnull().all():
                        logger.error(f"Found non-numeric values in the column {col}")
                        return

                n_points = len(df)
                if n_points > MAX_DATA_POINTS:
                    step = n_points // MAX_DATA_POINTS + 1
                    logger.info(f"Large dataset ({n_points} points). Subsampling with step {step}")
                    df = df.iloc[::step]

                self.time = df['time'].values
                self.intensity_11 = df['intensity_11'].values
                self.intensity_00 = df['intensity_00'].values
                self.intensity_1m1 = df['intensity_1m1'].values
                
              
                logger.info(f"Data loaded successfully: {len(self.time)} points")

            except Exception as e:
                logger.error(f"Error loading the CSV file: {str(e)}")


    # Part of code to create the graphs
        if len(self.time) > 0:
            try:
                # Main chart with sublots
                fig_main = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05)
                
                
                # Traccia order (0,0)
                fig_main.add_trace(
                    go.Scattergl(
                        x=self.time,
                        y=self.intensity_00,
                        mode='lines',
                        name='(0,0) Order',
                        line=dict(width=1, color='red')
                    ), row=1, col=1
                )
                
                # Traccia order (1,1)
                fig_main.add_trace(
                    go.Scattergl(
                        x=self.time,
                        y=self.intensity_11,
                        mode='lines',
                        name='(1,1) Order',
                        line=dict(width=1, color='blue')
                    ), row=2, col=1
                )
                
                # Traccia order (1,-1)
                fig_main.add_trace(
                    go.Scattergl(
                        x=self.time,
                        y=self.intensity_1m1,
                        mode='lines',
                        name='(1,-1) Order',
                        line=dict(width=1, color='green')
                    ), row=3, col=1
                )

                # Main chart layout
                fig_main.update_layout(
                    height=800,
                    width=1000,
                    title_text="RHEED Intensity Evolution",
                    hovermode="x unified",
                    showlegend=True,
                    xaxis=dict(fixedrange=False),  # Abilita zoom
                    yaxis=dict(fixedrange=False)    # Su tutti i subplots
                
                )


                # Adds annotations to axes
                fig_main.update_yaxes(title_text="(0,0) Order [J/cm²·s]", row=1, col=1)
                fig_main.update_yaxes(title_text="(1,1) Order [J/cm²·s]", row=2, col=1)
                fig_main.update_yaxes(title_text="(1,-1) Order [J/cm²·s]", row=3, col=1)
                fig_main.update_xaxes(title_text="Time [s]", row=3, col=1)

                self.figures.append(PlotlyFigure(
                    label='Main Plot',
                    figure=fig_main.to_plotly_json(),
                ))


                # Graph 4: All intensities superimposed
                fig_combined = go.Figure()
                fig_combined.add_trace(go.Scattergl(
                    x=self.time,
                    y=self.intensity_00,
                    name='(0,0) Order',
                    line=dict(color='red')
                ))
                fig_combined.add_trace(go.Scattergl(
                    x=self.time,
                    y=self.intensity_11,
                    name='(1,1) Order',
                    line=dict(color='blue')
                ))
                fig_combined.add_trace(go.Scattergl(
                    x=self.time,
                    y=self.intensity_1m1,
                    name='(1,-1) Order',
                    line=dict(color='green')
                ))

                fig_combined.update_layout(
                    title='Intensity Comparison',
                    xaxis_title='Time [s]',
                    yaxis_title='Intensity [J/cm²·s]',
                    hovermode='x unified',
                    height=400,
                    xaxis=dict(fixedrange=False),  # Permette zoom sull'assse x
                    yaxis=dict(fixedrange=False), # Permette zoom sull'asse y
                                        
                )

                self.figures.append(PlotlyFigure(
                    label='Combined Plot',
                    figure=fig_combined.to_plotly_json(),
                ))

            except Exception as e:
                logger.error(f"Errore nella generazione dei grafici: {str(e)}")
               


class PLDProcess(FabricationProcessStep, ArchiveSection):
    m_def = Section(
        a_eln={
            'hide': [
                'description', 
                'lab_id',
                'comment',
                'duration',
                'end_time',
                'start_time',
                'job_number',
                'location',
                'step_type',
                'definition_of_process_step',
                'name',
                'recipe_name',
                'recipe_file',
                'starting_date',
                'ending_date'
            ],
            'properties': {
                'order': [
                    'room',
                    'id_item_processed',
                    'target_material',
                    'thickness_measured',
                    'target_material_2', 
                    'thickness_measured_2',
                    'buffer_gas',
                    'chamber_pressure',
                    'temperature_target',
                    'heater_target_distance',
                    'repetition_rate',
                    'exposure_intensity',
                    'id_proposal',
                    'affiliation',
                    'operator',
                    'datetime',
                    'rheed_data_images',
                    'rheed_intensity_plot'
                ]
            }
        },
    )

    # Main fields
    room = Quantity(
        type=MEnum(['PLD chamber I', 'PLD chamber II']),
        description='Select the deposition chamber',
        a_eln={'component': 'EnumEditQuantity'}
    )
    
    id_item_processed = Quantity(
        type=str,
        description='Enter sample id',
        a_eln={'component': 'StringEditQuantity'}
    )
    
    target_material = Quantity(                                   
        type=MEnum(['LAO', 'Titanium', 'Terbium Scandate']),
        description='Select the main target material',
        a_eln={'component': 'EnumEditQuantity'}
    )
    
    thickness_measured = Quantity(
        type=np.float64,
        description='Enter the measured thickness of the layers deposited by the target',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'uc'
        },
        unit='uc'
    )
    
    target_material_2 = Quantity(
        type=MEnum(['No Target', 'LAO', 'Titanium', 'Terbium Scandate']),
        description='Select the secondary target material, if not present select No Target',
        a_eln={'component': 'EnumEditQuantity'}
    )
    
    
    thickness_measured_2 = Quantity(
        type=np.float64,
        description='Enter the measured thickness of the layers deposited by the target 2. If in target material 2 you have selected No Target leave this field blank',
        a_eln={
            'component': 'NumberEditQuantity', 
            'defaultDisplayUnit': 'uc',
        },
        unit='uc'
    )
    
    buffer_gas = Quantity(
        type=MEnum(['O2', 'Ar', 'N2']),
        description='Select process gas',
        a_eln={'component': 'EnumEditQuantity'}
    )
    
    chamber_pressure = Quantity(
        type=np.float64,
        description='Enter the pressure value inside the chamber',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'mbar'
        },
        unit='mbar'
    )
    
    temperature_target = Quantity(
        type=np.float64,
        description='Enter the heater temperature',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'celsius'
        },
        unit='celsius'
    )
    
    heater_target_distance = Quantity(
        type=np.float64,
        description='Enter target-heater distance',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'mm'
        },
        unit='mm'
    )
    
    repetition_rate = Quantity(
        type=np.float64,
        description='Enter the laser repetition rate',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'Hz'
        },
        unit='Hz'
    )
    
    exposure_intensity = Quantity(
        type=np.float64,
        description='Enter the exposure intensity',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'J/(cm**2*s)'},
        unit='J/(cm**2*s)'
    )
        
    id_proposal = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
        description='Enter the proposal id'
    )
    
    affiliation = Quantity(
        type=MEnum('NFFA-DI', 'iENTRANCE@ENL'),
        a_eln={'component': 'EnumEditQuantity'},
        description='Select the affiliation'
    )
    
    operator = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
        description='Enter the operator name'
    )

    
    datetime = Quantity(
        type=Datetime,
        a_eln={'component': 'DateTimeEditQuantity'},
        description='Enter the date and time of the process'
    )


    # RHEED image subsections
    rheed_data_images = SubSection(    
        section_def=RHEEDImage,
        repeats=True,
        description='Add RHEED images'
    )

    rheed_intensity_plot = SubSection(
        section_def=RHEEDIntensityPlot,
        description='RHEED intensity plot'
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)
        # Customizations of the class can be added inside normalize
        
        # Function that resets thickness_measured_2 if target_material_2 is "No Target"
        if self.target_material_2 == 'No Target' and self.thickness_measured_2 is not None:
            self.thickness_measured_2 = None
            logger.info("thickness_measured_2 è stato resettato perché target_material_2 è 'No Target'")
        



m_package.__init_metainfo__()
