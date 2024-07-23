
explain graphs + percentiles + what we have done so far
list of what we noticed + graphs
what we are going to do next

### General:
+ we would like to create new labels more specific to climate change to find out who talks about what
    + which aspects are mostly talked about or neglected
        + e.g. natural disasters, rising sea levels, loss of biodiversity, economic consequences, ...
    + who focuses on what
        + e.g. does the FT talk more about economic consequences than other newspapers?
    + [aspects_of_climate_change.md](../aspects_of_climate_change.md)

### Probability Distribution:
+ framing dimensions are normally distributed
    + all mean values are around 0
    + all values are between +/- 0.45
    + standard deviation is around 0.07
+ framing labels are more like an exponential distribution
    + different labels vary quite a lot
    + sometimes U-shaped
    + mean values are around 0.5
    + standard deviation is around 0.2


### Dimensions over time:
- Presse outliers:  
    - overall rather stable
    - 2015
    - a little bit: 2017, 2014
- IGO outliers:
    - definitely 2009, 2011
    - other years are in between the two
    - 2015 is somewhat similar to 2011
- NGO outliers:
    - 2017, 2019, 2016, 2021

### Presse:
+ different sources do not differ drastically
+ we noticed no notable differences between liberal (NYT, Guardian), moderate (FT, USAToday) and conservative (Telegraph) newspapers
+ FT 
    + most care, loyalty
        + definitely does not deny climate change and does not artificially sugarcoat it
        + but does not emphasize the harm
    + avg cheating
    + avg subversion?
    + more sanctity  
+ NYT
    + more harm
        + emphasizes the negative consequences of climate change more
        + often uses strong language (e.g. "catastrophic", "devastating", "kill", "threat")
        + at least this is my own judgement after comparing some FT, NYT articles, difference however is rather subtle imo
    + avg cheating
    + more betrayal
    + subversion changes a lot - avg i guess
    + more degradation
+ Telegraph
    + more harm
        + often quote/repeat the fears of pro-climate change people while emphasizing the negative consequences of proposed measures
        + e.g. quote "Sanctioning night scopes for culls will be endorsing something illegal across much of Europe."
        + seem to love quotes and anecdotes, often negative with strong language
        + though not all articles are completely negative 
    + most cheating
    + betrayal avg
    + subversion changes a lot - more subversion?
    + more degradation
        + conservative and liberal pretty identical
+ Guardian
    + more care
        + rather gentle language, not always though
            + e.g. "But it soon became apparent that things were not going to plan", "ministers started raising concerns.", "issues over 'loss and damage' emerged"
        + some climate "success stories"
        + optimistic language, e.g. "hope", "opportunity", "progress"
        + also likes quotes
    + most fairness
    + more loyalty
    + slightly more authority maybe?
    + avg sanctity
+ USAToday
    + most harm
        + most are pretty average but some articles almost read like a horror story
            + "Decades ago, London suffocated under poisonous smogs. Now, deadly air is back. ... Mayor Sadiq Khan now suggests children 
            should be given gas masks to protect their lungs. ... but it is poisonous … It is killing thousands of people" 
            + "Past a point of no return",  "It was a slaughterhouse", "The result is a carpet of highly flammable fuel throughout the West's forests and grasslands"
    + more cheating
    + most betrayal
    + avg subversion
    + degredation changed a lot - no clue

![](./plots/Presse_COP15_comparison.png)
![](./plots/Presse_COP21_comparison.png)
![](./plots/Presse_COP25_26_comparison.png)

### IGOs:
+ UN organizations are rather similar (dimension-wise)
    + UNFCCC, UNCDF, UNDP, REDD 
    + almost extreme
+ except for UNEP
    + UNEP seems rather average
    + more aligned with WB, IPCC
+ WB, WMO, IPCC mostly on the other end of the spectrum
+ holds for all dimensions (sanctity/degredation slightly less)
+ details
    + UNFCCC, UNCDF, UNDP, REDD
        + way more care, fairenss, loyalty, authority, sanctity
    + WB, IPCC
        + rather average except for degredation where they have the most
    + UNEP
        + behaves mostly like WB, IPCC
        + except for COP21, where it is more like UNFCCC, UNCDF, UNDP, REDD
            + which are not present for 2021
    + WMO
        + most harm, cheating, betrayal, subversion
        + average sanctity/degredation
    + WHO is pretty similar to UN (only 2021)

![](./plots/IGO_COP15_comparison.png)
![](./plots/IGO_COP21_comparison.png)
![](./plots/IGO_COP25_26_comparison.png)

### NGOs:
+ harder to compare since there are many different organizations with relatively few documents
+ WWF pretty average
+ Oxfam pretty extreme
    + lots of care, fairness, loyalty, authority, sanctity
    + more average in COP21
+ EDF weird
    + average in COP21, extreme in COP15, other extreme in COP25_26
+ NRDC rather average
    + lots of degredation, else average
+ Greenpeace
    + lots of cheating
    + average harm, loyalty, authority
    + slightly more degredation
+ FoEI
    + pretty average
+ EJF
    + lots of fairness, betrayal

