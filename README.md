# circadian_soundscape
This readme file was created by Confused_scientists for the AI+Environment Hackathon 2024

# GENERAL INFORMATION
Title of project: Analysing the Circadian Rhythm of the Amazon soundscape
Team: Confused_scientists

Name: Nivedita Varma Harisena
Institution: ETH Zurich
Email: nharisena@ethz.ch

Name: Leon Hauser
Institution: University of Zurich
Email: leon.hauser@geo.uzh.ch

Name: Varun Ghat Ravikumar
Institution: University of Zurich
Email: varunghat.ravikumar@uzh.ch

Name: Kien Nguyen
Institution: University of Zurich
Email: kien.nguyen@geo.uzh.ch

# INTRODUCTION
The following readme includes information on the data and code files submitted as part of the Hackathon. We also include code outputs for 3 sites in the Amazon as mentioned in the sampling_sites excel. The data we used for this was downloaded from the google drive shared folders:
	Dataset/Audio/Ingles/Primary1-including ultrasonic
	Dataset/Audio/Inha-be/ Inha-be Audiomoth 1
	Dataset/Audio/ParqueDasTribos

	
# DATA & FILE OVERVIEW
## Code files
1.	“Classification.py”- Includes implementation of an AST classification algorithm for audio data recovered from the 3 sites.
2.	“powerminusnoise.R”- Includes the implementation of “Power minus Noise” (PMN) index estimations that is a proxy for acoustic activity within a frequency range. The code outputs a .csv for each .wav input.
3.	“renametoadjustGMToff”- If input time steps are in GMT, this changes the file names to offset the output to the correct local time. 
4.	“Post-processing2_linepy”-Aggregates the outputs from “powerminusnoise.R” to get average, median and max values per time step in 24 hours for multiple days.
5.	“Graph_classfication.ipynb”- Creates Line plots with time in the x axis and species classification probabilities in the y axis for a given list of species.
6.	“Graph_PMN.ipynb”- Creates line plots with time in the x axis and PowerminusNoise estimates in the y axis for given frequency bins that can refer to the acoustic niche of different species. Also includes code to visualize the ‘colour’ of PMN over time by converting 3 chosen frequency bins to an RGB equivalent, allowing us to identify via colour which species group is most active in which time of the day based on the colour profiles.

## Data files
We also provide intermediate output from the 3 sites mentioned above. For each site you can find:
1.	Output from AST classification in “sitename_results.csv”
2.	Output for average, max and median PMN values in “sitename_PMN_average.csv”, “sitename_PMN_max.csv”  and “sitename_PMN_median.csv”
Where “sitename” is “Ingles”, “Inha-be” or “ParqueDasTribos”

### Relationship between files, if important: 
The output from “Classification.py” can be fed into “graph_classification.py” to get graphs of daily patterns of acoustic activity probabilities as predicted by the AST for crickets, frogs, animal, birds and human sounds.
The output from “powerminusnoise.R” must be fed into “Post-processing2_line.py” to get Output 2 as mentioned above. This should then be processed with “renametoadjustGMToff.py” and the output from which can be used in “Graph_PMN.ipynb” to create visualisations. Examples of this is included later in this readme file. 
Additionally, visualization of the output has also been implemented via our Huggingface interface: https://huggingface.co/spaces/trans-farmer/circadian_rhythm_soundscape

# Example output

1.	Graphs from AST classification:  
<img loading="lazy" width="30px" src="[/RGB_cirlce_out.jpg]" alt="RGB_cirlce_out.jpg" />

2.	Graphs from PowerminusNoise estimates:


## Data-specific information for:
1.	“sitename_results.csv”: 
2.	“sitename_PMN_average.csv”, “sitename_PMN_max.csv”  and “sitename_PMN_median.csv”: includes information on frequency bins and corresponding
