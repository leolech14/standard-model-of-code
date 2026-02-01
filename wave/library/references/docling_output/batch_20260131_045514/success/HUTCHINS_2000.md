## Distributed Cognition: Toward a New Foundation for Human-Computer Interaction Research

JAMES HOLLAN, EDWIN HUTCHINS, and DAVID KIRSH University of California, San Diego

We are quickly passing through the historical moment when people work in front of a single computer, dominated by a small CRT and focused on tasks involving only local information. Networked computers are becoming ubiquitous and are playing increasingly significant roles in our lives and in the basic infrastructures of science, business, and social interaction. For human-computer interaction to advance in the new millennium we need to better understand the emerging dynamic of interaction in which the focus task is no longer confined to the desktop but reaches into a complex networked world of information and computer-mediated interactions. We think the theory of distributed cognition has a special role to play in understanding interactions between people and technologies, for its focus has always been on whole environments: what we really do in them and how we coordinate our activity in them. Distributed cognition provides a radical reorientation of how to think about designing and supporting human-computer interaction. As a theory it is specifically tailored to understanding interactions among people and technologies. In this article we propose distributed cognition as a new foundation for human-computer interaction, sketch an integrated research framework, and use selections from our earlier work to suggest how this framework can provide new opportunities in the design of digital work materials.

Categories and Subject Descriptors: D.2.1 [ Software Engineering ]: Requirements/SpecificationsMethodologies (e.g., object-oriented, structured); H.1.2 [ Models and Principles ]: User/Machine Systems; H.5.2 [ Information Interfaces and Presentation ]: User InterfacesEvaluation/methodology ; H.5.3 [ Information Interfaces and Presentation ]: Group and Organization InterfacesTheory and models ; Evaluation/methodology

General Terms: Design, Human Factors, Theory

Additional Key Words and Phrases: Cognitive science, distributed cognition, ethnography, human-computer interaction, research methodology

This work was supported by grant #9873156 from the National Science Foundation. Additional support was provided by Intel, Sony, and Sun.

Authors' address: Distributed Cognition and HCI Laboratory, Department of Cognitive Science, University of California, San Diego, La Jolla, CA 92093-0515; email: {hollan; hutchins; kirsh}@hci.ucsd.edu.

Permission to make digital/hard copy of part or all of this work for personal or classroom use is granted without fee provided that the copies are not made or distributed for profit or commercial advantage, the copyright notice, the title of the publication, and its date appear, and notice is given that copying is by permission of the ACM, Inc. To copy otherwise, to republish, to post on servers, or to redistribute to lists, requires prior specific permission and/or a fee.

© 2000 ACM 1073-0516/00/0600-0174 $5.00

ACM Transactions on Computer-Human Interaction, Vol. 7, No. 2, June 2000, Pages 174-196.

## 1. INTRODUCTION

As computation becomes ubiquitous, and our environments are enriched with new possibilities for communication and interaction, the field of human-computer interaction confronts difficult challenges of supporting complex tasks, mediating networked interactions, and managing and exploiting the ever increasing availability of digital information. Research to meet these challenges requires a theoretical foundation that is not only capable of addressing the complex issues involved in effective design of new communication and interaction technologies but also one that ensures a human-centered focus. In this article we argue that the theory of distributed cognition [Hutchins 1995a; Norman 1993; Saloman 1993] provides an effective theoretical foundation for understanding human-computer interaction and a fertile framework for designing and evaluating digital artifacts.

The theory of distributed cognition, like any cognitive theory, seeks to understand the organization of cognitive systems. Unlike traditional theories, however, it extends the reach of what is considered cognitive beyond the individual to encompass interactions between people and with resources and materials in the environment. It is important from the outset to understand that distributed cognition refers to a perspective on all of cognition, rather than a particular kind of cognition. It can be distinguished from other approaches by its commitment to two related theoretical principles.

The first of these principles concerns the boundaries of the unit of analysis for cognition. In every area of science, the choices made concerning the boundaries of the unit of analysis have important implications. In traditional views of cognition the boundaries are those of individuals. Sometimes the traditionally assumed boundaries are exactly right. For other phenomena, however, these boundaries either span too much or too little. Distributed cognition looks for cognitive processes, wherever they may occur, on the basis of the functional relationships of elements that participate together in the process. A process is not cognitive simply because it happens in a brain, nor is a process noncognitive simply because it happens in the interactions among many brains. For example, we have found it productive to consider small sociotechnical systems such as the bridge of a ship [Hutchins 1995a] or an airline cockpit [Hutchins 1995b; Hutchins and Klausen 1996; Hutchins and Palen 1997] as our unit of analysis. In distributed cognition, one expects to find a system that can dynamically configure itself to bring subsystems into coordination to accomplish various functions. A cognitive process is delimited by the functional relationships among the elements that participate in it, rather than by the spatial colocation of the elements.

The second principle that distinguishes distributed cognition concerns the range of mechanisms that may be assumed to participate in cognitive processes. Whereas traditional views look for cognitive events in the manipulation of symbols inside individual actors, distributed cognition

•

looks for a broader class of cognitive events and does not expect all such events to be encompassed by the skin or skull of an individual. For example, an examination of memory processes in an airline cockpit shows that memory involves a rich interaction between internal processes, the manipulation of objects, and the traffic in representations among the pilots. A complete theory of individual memory by itself is insufficient to understand how this memory system works. Furthermore, the physical environment of thinking provides more than simply additional memory available to the same processes that operate on internal memories. The material world also provides opportunities to reorganize the distributed cognitive system to make use of a different set of internal and external processes.

In distributed cognition, one expects to find a system that can dynamically configure itself to bring subsystems into coordination to accomplish various functions. A cognitive process is delimited by the functional relationships among the elements that participate in it, rather than by the spatial colocation of the elements. When one applies these principles to the observation of human activity 'in the wild,' at least three interesting kinds of distribution of cognitive process become apparent:

- -Cognitive processes may be distributed across the members of a social group.
- -Cognitive processes may involve coordination between internal and external (material or environmental) structure.
- -Processes may be distributed through time in such a way that the products of earlier events can transform the nature of later events.

In order to understand human cognitive accomplishments and to design effective human-computer interactions it is essential that we grasp the nature of these distributions of process. In the next section we elaborate a distributed cognition approach before describing in Section 3 how the theory of distributed cognition may provide a new foundation for HCI and in Section 4 how it can help the design of new digital work materials.

## 2. A DISTRIBUTED COGNITION APPROACH

## 2.1 Socially Distributed Cognition

The idea of socially distributed cognition, prefigured by Roberts [1964], is finding new popularity. Anthropologists and sociologists studying knowledge and memory, AI researchers building systems to do distributed problem solving, social psychologists studying small group problem solving and jury decision making, organizational scientists studying organizational learning, philosophers of science studying discovery processes, and economists and political scientists exploring the relations of individual and group rationality, all have taken stances that lead them to a consideration of the cognitive properties of societies of individuals. One idea that is

•

emerging is that social organization is itself a form of cognitive architecture.

The argument is as follows. Cognitive processes involve trajectories of information (transmission and transformation), so the patterns of these information trajectories, if stable, reflect some underlying cognitive architecture. Since social organization-plus the structure added by the context of activity-largely determines the way information flows through a group, social organization may itself be viewed as a form of cognitive architecture.

If this view is accepted, it has an odd consequence: we can use the concepts, constructs, and explanatory models of social groups to describe what is happening in a mind. Thus for instance, Minsky, in Society of Mind [Minsky 1986], argues that '...each brain contains hundreds of different types of machines, interconnected in specific ways which predestine that brain to become a large, diverse society of partially specialized agencies.' He then goes on to examine how coalitions of these agents coordinate their activities to achieve goals. The implication, of course, is that the cognition of an individual is also distributed.

Distributed cognition means more than that cognitive processes are socially distributed across the members of a group. It is a broader conception that includes phenomena that emerge in social interactions as well as interactions between people and structure in their environments. This perspective highlights three fundamental questions about social interactions: (1) how are the cognitive processes we normally associate with an individual mind implemented in a group of individuals, (2) how do the cognitive properties of groups differ from the cognitive properties of the people who act in those groups, and (3) how are the cognitive properties of individual minds affected by participation in group activities?

## 2.2 Embodied Cognition

A second tenet of the distributed cognition approach is that cognition is embodied. It is not an incidental matter that we have bodies locking us causally into relations with our immediate environments. Causal coupling is an essential fact of cognition that evolution has designed us to exploit.

In recent years this idea has gained increasingly strong support [Brooks 1991; Clark 1997; Kirsh 1995; 1996; Lakoff 1987; Maturana and Varella 1987; Thelen 1995; Turvey et al. 1981; Varlea et al. 1991]. Minds are not passive representational engines, whose primary function is to create internal models of the external world. The relations between internal processes and external ones are far more complex, involving coordination at many different time scales between internal resources-memory, attention, executive function-and external resources-the objects, artifacts, and at-hand materials constantly surrounding us.

From the perspective of distributed cognition, the organization of mindboth in development and in operation-is an emergent property of interactions among internal and external resources. In this view, the human body and the material world take on central rather than peripheral roles. As

•

Andy Clark put it, 'To thus take the body and world seriously is to invite an emergentist perspective on many key phenomena-to see adaptive success as inhering as much in the complex interactions among body, world, and brain as in the inner processes bounded by the skin and skull' [Clark 1997].

For the design of work environments, this means that work materials are more than mere stimuli for a disembodied cognitive system. Work materials from time to time become elements of the cognitive system itself. Just as a blind person's cane or a cell biologist's microscope is a central part of the way they perceive the world, so well-designed work materials become integrated into the way people think, see, and control activities, part of the distributed system of cognitive control.

## 2.3 Culture and Cognition

A third tenet of the theory of distributed cognition is that the study of cognition is not separable from the study of culture, because agents live in complex cultural environments. This means, on the one hand, that culture emerges out of the activity of human agents in their historical contexts, as mental, material and social structures interact, and on the other hand, that culture in the form of a history of material artifacts and social practices, shapes cognitive processes, particularly cognitive processes that are distributed over agents, artifacts, and environments. Hutchins treats this at length in his recent book, Cognition in the Wild [Hutchins 1995a].

Permitting the boundary of the unit of analysis to move out beyond the skin situates the individual as an element in a complex cultural environment [Cole 1996; Shore 1996; Strauss and Quinn 1998]. In doing this, we find that cognition is no longer isolated from culture or separate from it. Where cognitive science traditionally views culture as a body of content on which the cognitive processes of individual persons operate, in the distributed cognition perspective, culture shapes the cognitive processes of systems that transcend the boundaries of individuals [Hutchins 1995a].

At the heart of this linkage of cognition with culture lies the notion that the environment people are embedded in is, among other things, a reservoir of resources for learning, problem solving, and reasoning. Culture is a process that accumulates partial solutions to frequently encountered problems. Without this residue of previous activity, we would all have to find solutions from scratch. We could not build on the success of others. Accordingly, culture provides us with intellectual tools that enable us to accomplish things that we could not do without them. This is tremendously enabling. But it is not without cost. For culture may also blind us to other ways of thinking, leading us to believe that certain things are impossible when in fact they are possible when viewed differently.

Distributed cognition returns culture, context, and history to the picture of cognition. But these things cannot be added onto the existing model of cognitive processes without modifying the old model. That is, the new view of culturally embedded cognition requires that we remake our model of the individual mind.

## 2.4 Ethnography of Distributed Cognitive Systems

A major consequence of the tenets of embodiment-cultural immersion and social distribution-is that we need a new kind of cognitive ethnography to properly investigate the functional properties of distributed cognitive systems. The ethnographic methods associated with cognitive anthropology in the 1960's and 1970's focused on meaning systems: especially, but not exclusively, the meanings of words [Agar 1986; Tyler 1969; Werner and Schoepfle 1987]. Meanings were sought in the contents of individual minds [Hutchins 1980; Kronenfeld 1996; Wallace 1970]. The ethnography of distributed cognitive systems retains an interest in individual minds, but adds to that a focus on the material and social means of the construction of action and meaning. It situates meaning in negotiated social practices, and attends to the meanings of silence and the absence of action in context as well as to words and actions [Hutchins and Palen 1997].

The theoretical emphasis on distributed cognitive processes is reflected in the methodological focus on events. Since the cognitive properties of systems that are larger than an individual play out in the activity of the people in them, a cognitive ethnography must be an event-centered ethnography. We are interested not only in what people know, but in how they go about using what they know to do what they do. This is in contrast to earlier versions of cognitive ethnography which focused on the knowledge of individuals and largely ignored action.

Cognitive ethnography is not any single data collection or analysis technique. Rather it brings together many specific techniques, some of which have been developed and refined in other disciplines (e.g., interviewing, surveys, participant observation, and video and audio recording). Which specific technique is applied depends on the nature of the setting and the questions being investigated. Because of the prominence of events and activity in the theory, we give special attention to video and audio recording and the analysis of recordings of events [Goodwin and Goodwin 1996; Suchman 1987]. In human-computer interaction settings we expect automated recording of histories of interaction [Hill and Hollan 1994] to become an increasingly important source of data.

The theory holds that cognitive activity is constructed from both internal and external resources, and that the meanings of actions are grounded in the context of activity. This means that in order to understand situated human cognition, it is not enough to know how the mind processes information. It is also necessary to know how the information to be processed is arranged in the material and social world. This, in turn, means that there is no substitute for technical expertise in the domain under study. This is why participant observation is such an important component of cognitive ethnography.

The approach to human-computer interaction we propose here requires researchers to make a real commitment to a domain. If one is to talk to experts in a meaningful way about their interactions with structure in their task environments, one must know what that structure is and how it

•

•

may be organized. One must also know the processes actors engage in and the resources they use to render their actions and experiences meaningful. This perspective provides new insights for the design of conceptually meaningful tools and work environments. It implies that their design should take into account the ways actors can achieve coordination with the dynamic behavior of active work materials.

As we will discuss later, design of new digital displays and interfaces risks inadvertently destroying many of the most valuable aspects of current ways of doing things because we do not understand how they work. For example, consider the development of the airspeed tape in state-of-the-art cockpits. The overt function of the airspeed indicator is to show the pilot the airspeed of the aircraft. But an analysis of how airspeed instruments are actually used shows that the way pilots use airspeed instruments is more complex and more interesting than might have been suspected [Hutchins 1995b]. The features that the pilot uses in the round-dial instrument have been inadvertently removed from the airspeed tapes of all of the current state-or-the-art cockpits (Airbus, McDonnell Douglas, Boeing, Fokker). This is not an inevitable consequence of using digital display technology in the cockpit; it is, rather, a consequence of design that is not based on solid cognitive ethnography. The very newest airline cockpit (that in the Boeing 737-700) contains a replication of the old electromechanical instrument, now rendered in a digital display. This is probably better than the digital airspeed tapes, but one wonders why the designers could not get the appropriate behavior in the tapes, and why, in order to get the right behavior, they had to resort to a literal copy of the old instrument.

We believe that what was lacking was a method that could identify the critical features of the interactions between pilots and the old instrument and a theoretical language in which these features could be expressed in a sufficiently abstract form that they could be moved to a very different display format. By combining observations of pilots in flight with study of operations manuals, interviews with pilots, and participation in the training programs for two modern airliners, Hutchins was able to establish that pilots use the airspeed indicator dial as a material anchor for a conceptual space of meaningful airspeeds. They only rarely think of the speed as a number. Instead, they use the spatial structure of the display to make perceptual inferences about relations among actual and desired speeds.

While digital display design is an important research topic, and one with which we are concerned, what we are proposing is more fundamental: a research framework that integrates distributed cognition theory with methods for design of digital work materials.

## 3. AN INTEGRATED FRAMEWORK FOR RESEARCH

The field of human-computer interaction could certainly benefit from an integrated research framework. The framework we propose contains the elements shown in Figure 1. Although this entire integrated program has never before been assembled, our previous work has led us to this inte-

Distributed Cognition

Experiment

→

Ethnography

•

Fig. 1. Integrated research activity map.

<!-- image -->

grated program, and it promises to open up new opportunities for research in cognitive science and for designing new forms of human-computer interaction.

How then do the parts of this program fit together? The general idea is as follows. Distributed cognition theory identifies a set of core principles that widely apply. For example,

- -people establish and coordinate different types of structure in their environment
- -it takes effort to maintain coordination
- -people off-load cognitive effort to the environment whenever practical
- -there are improved dynamics of cognitive load-balancing available in social organization.

These principles serve to identify classes of phenomena that merit observation and documentation. Cognitive ethnography has methods for observing, documenting, and analyzing such phenomena, particularly information flow, cognitive properties of systems, social organizations, and cultural processes. Because cognitive ethnography is an observational field, the inferences we would like to draw are at times underconstrained by the available data. In these cases, the findings of cognitive ethnography may suggest 'ethnographically natural' experiments to enrich our data.

The principles of distributed cognition are also at play in these experiments because the point of experimentation should be to make more precise the impact of changes in the naturally occurring parameters that theory tells us are important. As these three areas-principles, ethnography, and experiment-are elaborated, they mutually constrain each other and offer prescriptive information on the design of work materials. To be sure, the matter is more complicated. Work materials are themselves part of workplaces, and themselves constitute important changes in the distributed cognition environment. So the introduction of a new work material is itself

•

a form of ethnographic experiment, which allows us to test and revise the theory. But, in general, we give pride of place to the principles of distributed cognition, for it is these that inform experiment, ethnographic observation and design of work materials and workplaces.

It is worth elaborating these relations. Consider how cognitive ethnography is used. Cognitive ethnography seeks to determine what things mean to the participants in an activity and to document the means by which the meanings are created. This is invariably revealing and often surprising. For example, in the world of aviation and ship navigation we have documented many cases of use of structure that were not anticipated by the designers of the tools involved. Experts often make opportunistic use of environmental structure to simplify tasks. A simple example is that pilots routinely display the test pattern on the weather radar as a reminder that a final fuel transfer is in progress. There is no method other than observation that can discover these sorts of facts of behavior, and no other method that can teach us what really matters in a setting.

In order to make real-world observations, it is necessary to establish rapport with the members of a community. While the skills required to do this are not normally part of a curriculum in cognitive science, they are as essential as the methods of experimental design. Cognitive ethnography feeds distributed cognition theory by providing the corpus of observed phenomena that the theory must explain. Most cognitive theories seek to explain experimental data. We believe there should be a single theory that covers cognition as it occurs in all settings. An experiment is, after all, just another socially organized context for cognitive performance. This means not only that we look at so-called real-world settings, but that we look differently at experiments, seeing them as settings in which people make use of a variety of material and social resources in order to produce socially acceptable behavior.

While the study of cognition in the wild can answer many kinds of questions about the nature of human cognition in real workplaces, the richness of real-world settings places limits on the power of observational methods. This is where well-motivated experiments come in. For instance, we recently observed that when children try to build a model using small parts, they regularly modularized the problem in ways that were helpful at the time but had to be dismantled later. This real-world problem solving uses these parts to act out ideas, to help the child explore and understand the problem. Having observed this in natural settings we can set about designing more constrained experiments which test specific aspects of this 'exploratory' behavior.

Design enters the story in several ways. First, ethnography offers clever ways of getting things done that can be incorporated in new designs. New uses can be found for old strategies, and techniques effective in one setting may be transferred to another. Experiments can refine the theory of distributed cognition which in turn can be applied to improve design. Finally, since the design process creates new tools for workplaces, there are new structures and interactions to study.

•

This loop from observation to theory to design and back to new ethnographic observations is an important cycle of activity in our framework. The design process, by virtue of posing design decisions, may also reveal novel aspects of behavior that should be attended to by cognitive ethnography or experimental studies. This forms yet another cycle of activity that can be used to refine each element in turn as the elements of the cycle interact with one another. The many loops and feedback circuits in the activity map reflect the multiple iterative processes involved in the successive refinement of theory, methods, and products.

Portions of the integrated approach have appeared in our previous work, but, to date, the entire activity has not been applied to a single problem domain. In the following sections we summarize our earlier work on a number of projects, and show in each case the overlapping subsets of the elements of the activity that were conducted, and the new opportunities that are presented by assembling the complete integrated research system.

## 3.1 Ship Navigation

In the 1980's, Hutchins did an extended cognitive ethnography of navigation aboard US Navy ships [Hutchins 1995a; Seifert and Hutchins 1992]. The very notion of distributed cognition and the need for cognitive ethnography arose from the observation that the outcomes that mattered to the ship were not determined by the cognitive properties of any single navigator, but instead were the product of the interactions of several navigators with each other and with a complex suite of tools. That work developed distributed cognition theory and extended the methods of cognitive ethnography. It examined the history of navigation practice in two very different cultural traditions to show how a single computational level of description could cover systems that had radically different representational assumptions and implementational means. It examined the details of tool use, showing how the cognitive processes required to manipulate a tool are not the same as the computations performed by manipulating the tool. It documented the social organization of work and showed how learning happened both in individuals and at the organizational level.

The integrated process we are proposing here could take that work much further. The observations of the practices of navigation suggest experiments. For example, when accomplished navigators talk about bearings expressed in numbers of degrees, they often report, that in addition to thinking of the three-digit number, they feel a bearing as a direction in space relative to the position of their body. A navigator facing northeast may say that a bearing of 135 degrees true feels to be off to his right side. Some observed instances of navigators detecting errors appear to involve this sort of cross-modal representation. Since error detection is a key cognitive property of this system, it would be nice to know how this actually works. It is not possible to know from observation alone what role such representations might play in the navigation task. An experiment using expert subjects could shed light on this important process.

While Hutchins' work on ship navigation did not include any design activities, it could also be used as a basis for the design of electronic charting tools (an area of considerable interest to the Navy and the Coast Guard). An ethnography of the use of these new tools would be the beginning of the next phase of the cycle of research activity.

## 3.2 Airline Cockpit Automation

In the late 1980's, Hutchins moved his primary field location from the bridges of ships to the cockpits of commercial airliners. Since then he and his students have continued to refine the distributed cognition theory by applying it to cockpit [Hutchins 1995b; Hutchins and Klausen 1996; Hutchins and Palen 1997] and air traffic control [Halverson 1995]. This work included an extensive cognitive ethnography of airline pilots including observations in the jumpseat of airliners in revenue flight, completion of training programs for state-of-the-art airliners, and work with airline training departments on the design of training programs. Based on a theoretical interpretation of the ethnographic findings, Hutchins designed a graphical interface to the autoflight functions of the Boeing 747-400 [Hutchins 1996]. That interface uses direct-manipulation technology, originally developed in the STEAMER project [Hollan et al. 1984], which is now nearly 20 years old. We now have the opportunity to apply the very latest technology to the problem of making the behavior of the autoflight system visible to the pilots.

Based on the ethnographic study of the use of both conventional and digital airspeed indicators, we have also designed a new digital airspeed tape. It takes advantage of the power of the computational medium (automatic annotation of target airspeeds, acceleration indications, etc.), but also maintains the most useful features of the previous generation of electromechanical devices. Pilots using electromechanical airspeed indicators develop perceptual strategies that rely on the perceptual salience of the spatial location of the airspeed indicator needle in a space of meaningful speeds. Our new instrument not only preserves this property; it makes it perceptually even more salient than was the case in the original. These design alternatives raise a number of important questions that can only be resolved by experimental investigation. For example, the ethnographic analysis indicates that since pilots rarely read the airspeed as a number, it may be possible for them to recover much of the information they need from the older designs without bringing the instrument into foveal vision. In our integrated approach, we are now in a position to complement the ethnographic, theoretic, and design activities with experimental investigations of pilot eye movements while using the alternative designs.

## 3.3 Beyond Direct Manipulation

It is possible to create virtual social and material environments that have different properties than real environments. Hollan and Stornetta [1992] discuss how an unquestioned presupposition of the efficacy of imitating

ACM Transactions on Computer-Human Interaction, Vol. 7, No. 2, June 2000.

•

face-to-face communication restricts current human-computer interaction work on supporting informal communication. By paying close attention to how people actually exploit real environments, and describing those phenomena in appropriate theoretical terms, we can see how to go beyond the simple replication of felicitous features of the real world. An important research issue for the field of human-computer interaction is how to move beyond current direct-manipulation interfaces.

One key focus of research based on distributed cognition is the nature of representations and the ways that people use representations to do work. Traditional information processing psychology focuses on symbols as tokens that refer to something other than themselves, but pays little attention to strategies people may develop to exploit the physical properties of the representing tokens themselves. Our cognitive ethnographies show us that people often shift back and forth between attending to the properties of the representation and the properties of the thing represented, or intentionally blur the two. These strategies of shifting in and out of the symbolic stance support some very interesting cognitive processing. For example, Hazlehurst [1994] studied Swedish fishermen who coordinate their actions with other boats in a pair-trawl by interpreting and talking about what appears on a false-color sonar display. They talk about seeing flecks and sprinkles , as well as fish . And they mix the two kinds of talk as in that fleck is dense enough to set the net upon .

Hutchins and Palen [1997] looked at how a meaningfully constructed space (the flight engineer's panel in a Boeing 727 airliner) and gesture and speech are all woven together in a brief cockpit episode in which the flight engineer explains to the captain and first officer that they have a fuel leak. He interacts with the panel both as if it is the fuel system it depicts, and, at other times, as if it is just a representation of the fuel system (when he flicks a gauge with his finger to get the needle to move, for example). These shifts from attending to the representation to attending to the thing represented, whether in communication or in individual action, provide a range of cognitive outcomes that could not be achieved if representations were always only taken as representations of something else, and not as things in themselves.

Given the primary role of representation in interfaces to computational systems, there are likely to be many opportunities to exploit such shifts. That is, it might be possible to do one kind of cognitive work on the representations as things in themselves and another kind of cognitive work interacting with the representations as stand-ins for the things they represent. In direct-manipulation interfaces the objects on-screen are meant to be so closely coupled to the actual computational objects we are dealing with that we are supposed to feel as if we are manipulating the real objects themselves and not just their stand-ins. To achieve this feeling of immediacy [Hutchins et al. 1985], it is essential that meaningful interface actions have meaningful counterparts in the system. Thus, in dragging an icon of a file from one folder to another we are not to think we are just moving icons, but rather moving the actual folders and all their contents.

There are limits, however, to how well a representation can resemble the thing it represents. For instance, many of the actions we perform on icons have no meaningful correlate when we consider their referent. This is especially true when we consider the way we can change the spatial relations between icons. For example, when we move an image of a hard drive to a more convenient position on the screen where could we be moving the real hard drive to? Distributed cognition theory makes this otherwise isolated observation an instance of an important class of events: those in which people manipulate the properties of a representation to encode information that does not pertain to and is not about the thing that the representation represents.

Screen space often has no natural correlate in physical space. Thus when we rearrange the layout of directory windows, it makes no sense to ask whether we have brought those directories closer on the hard drive. The screen as desktop allows us to interpret such actions as analogous to shifting folders about on a flat desk, but folders can be made to pop in and out of existence, or to change in size, which again has no easy counterpart in the real world. The same applies when one changes the way files in a directory are displayed. It is certainly conceivable that alphabetizing, sorting by recency, or sorting by size are actions that change the order in which files are written on a disk. But it is more plausible to think of these as actions on the labels of files, not as actions on the files themselves.

Because we manipulate icons in icon space it is possible to take advantage of the way they are displayed to help us further simplify our activity. We can opportunistically exploit structural possibilities of the interface. Files may be left near the trash can to remind us that we need to delete them. Files that are to be used for a single project can be bunched together, or aliased so that they appear to be in two folders at once.

As users become more familiar with an environment they situate themselves more profoundly. We believe that insights concerning the way agents become closely coupled with their environments have yet to be fully exploited in interface design. As we build richer, more all-encompassing computational environments it becomes more important than ever to understand the ways human agents and their local environments are tightly coupled in the processing loops that result in intelligent action.

Discovering new models of active representations is fundamental to the future of human-computer interaction. Hollan et al. [1997] have proposed an informational physics model. Such models specify rules for how information presents and advertises itself and how it reacts to a changing environment. Changes can include the availability of alternative perceptual access routes, the presence of other informational entities, and the evolving nature of users' tasks, histories of interaction, and relationships with other information-structuring entities.

The research framework we proposed here and our previous theoretical, ethnographic, and design efforts lead one to address questions such as

-How then can we design representations to facilitate their flexible use?

ACM Transactions on Computer-Human Interaction, Vol. 7, No. 2, June 2000.

•

- -How can we make representations more active so that they help users see what is most relevant to deciding what to do next?
- -How can we shift the frame of interpretation so as to achieve a better conceptualization of what is going on and what ought to be done?

One way to address each of these questions is to specifically focus on creation of virtual social and material environments that go beyond mere imitation of the felicitous features of the real world to exploit the felicitous features of a computational world.

## 3.4 History-Enriched Digital Objects

Just as computation can be used to create potentially more flexible and effective active representations, it can also be used to allow representations to record their history of use and make that history available in ways that inform tasks and facilitate interaction. We think that automated gathering of activity histories provides rich opportunities for pursuing the eventcentered ethnography we are proposing.

In interaction with objects in the world, history of use is sometimes available to us in ways that inform our interactions with them. For example, a well-worn section of a door handle suggests where to grasp it. A new paperback book opens to the place we last stopped reading. The most recently used pieces of paper occupy the tops of piles on our desk. The physics of the world is such that at times the histories of use are perceptually available to us in ways that support the tasks we are doing. While we can mimic these mechanisms in interface objects, of potentially greater value is exploiting computation to develop new history of interaction mechanisms that dynamically change to reflect the requirements of different tasks.

Studies of experts working in complex environments [Hutchins 1995b] have shown that use-histories are sometimes incorporated in cognitively important processes. The side effects of use often provide resources for the construction of expert performance. Unfortunately, these supports for expert performance are sometimes actively, but mistakenly, designed out of 'clean' and 'simple' digital work environments. A striking example of this is the cockpit of the Airbus A-320 aircraft as discussed in Gras et al. [1991]. By recognizing the functions of use-histories in simple media, we can exploit digital media to provide additional support in ways that are simply not possible with static media.

Digital objects can encode information about their history of use. By recording the interaction events associated with use of digital objects (e.g., reports, forms, source code, manual pages, email, spreadsheets) it becomes possible to display graphical abstractions of the accrued histories as parts of the objects themselves. For example, we can depict on source code its copy history so that developers can see that a particular section of code was created based on a copy of other code and thus perhaps be led to correct a

bug not only in code being debugged but also in the code from which it was derived.

In earlier efforts [Hill et al. 1992], we explored the use of attributemapped scroll bars as a mechanism to make the history of interaction with documents and source code available. Hollan and his colleagues modified various editors to maintain detailed interaction histories. Among other things, they recorded who edited or read various sections of documents or code as well as the length of time they took. Histories of those interactions were graphically made available in the scroll bar. These graphical depictions identified and highlighted sections that had been edited and who had edited them. Presenting this in the scroll bar made effective use of limited display real estate. To investigate any particular section, users need only click on that section of the scroll bar. Similarly, we and others [Eick et al. 1992] have explored representing histories of interaction on source code itself.

We have also developed other applications of history-enriched digital objects [Hill and Hollan 1994]. For example, one can apply the idea to menus so that the accrued history of menu choices of other users of a system are indicated by making the more commonly used menu items brighter. Or one can present spreadsheets such that the history of changes to items are graphically available, and thus sections of budgets currently undergoing modification are distinguished. We have also recorded the time spent in various editor buffers to enable visualizations of the activity histories of tasks associated with those buffers.

Records of the amount of time spent reading wire services, netnews, manual pages, and email messages can be shared to allow people to exploit the history of others' interactions. One can, for example, be directed to news stories that significant others have spent considerable time reading or to individuals who have recently viewed a manual page that you are currently accessing. There are, of course, complex privacy issues involved with recording and sharing this kind of data. Such data, in our view, should belong to users, and it should be their decision what is recorded and how it might be shared. Encryption should be used to prevent data from being obtained without the owner's permission.

The rich data resulting from recording histories of interaction and required to support active representations that conform to different use contexts is a crucially important area of research and potential resource upon which to base the design of future digital work environments. The integrated framework we propose here highlights the importance of ethnographic analysis of current use histories and encourages us to expand our exploration of digital artifacts that capture their use histories. But capturing such histories is only the first step in being able to effectively exploit them. The framework we are advocating suggests that we examine the activities of those systems at multiple scales.

•

The observation that we move closer to items we wish to know more about, or that if we cannot get closer, we view them through magnifying optics, is so commonplace that it seems unworthy of mention. Yet, this simple and powerful idea can be exploited in computational media in ways that other media do not allow.

Pad 11 [Bederson and Hollan 1994; Bederson et al. 1996] is an experimental software system to support exploration of dynamic multiscale interfaces. It is part of our research program to move beyond mimicking the mechanisms of earlier media to more effectively exploit computational mechanisms. It provides a general-purpose substrate for creating and interacting with structured information based on a zoomable interface. Pad 11 workspaces are large in extent and resolution, allowing objects to be placed at any location and at any size. Zooming and panning are supported as the fundamental interaction techniques.

Pad 11 provides multiscale interface development facilities. These include portals to support multiple views, lenses to filter and furnish alternative views, search techniques to allow one to find information that matches selected characteristics and easily move to it, history markers and hypertext links to support navigation, layout and animation facilities, and other experimental multiscale interface techniques and tools.

While Pad 11 provides a powerful substrate for creating multiscale work materials, here we mention only one example. PadPrints [Hightower et al. 1998] is a Pad 11 application linked with Netscape that functions as a navigation aid for web-based browsing. As a user follows links in the browser, a multiscale map of the history of traversals is maintained by PadPrints. The graphical views of pages can be used to select previously visited pages and are ideal candidates for visually representing the historyof-use information mentioned earlier. As a navigation aid, PadPrints exploits multiscale facilities for both representation and interaction. We have shown it to be more effective than traditional browsers [Hightower et al. 1998] in a variety of common information search tasks.

Information-intensive workplaces can be naturally viewed within a multiscale space. Dynamic multiscale spaces are particularly appropriate for hierarchical information because items that are deeper in the hierarchy can be made smaller, yet because they are still in view they can easily be accessed by zooming. Similarly, the time structure of many informationbased tasks is hierarchical in nature and fits well with multiscale representations.

Embedding Pad 11 research within the distributed-cognition framework we propose here has important consequences. It helps us realize that some of what is powerful about multiscale representations comes from how individuals and groups adapt. As we discuss below, careful observation demonstrates that we constantly adapt to our environments at different spatiotemporal scales. Individually we adapt through interaction and creating scaffolding; collectively we adapt through culture and intelligent

•

coordination. The very flexible multiscale representations that Pad 11 makes possible allow us to explore representations that might better fit these differing spatiotemporal scales.

Distributed cognition encourages us to look at functional organizations that soften traditional boundaries between what is inside and what is outside. Because of the highly interactive nature of Pad 11 interfaces there is a rich interplay of cognitive processing, activity structure, and dynamic representational changes. How people manipulate the multiscale space and the multiscale objects within it is of particular interest. For example, when using PadPrints, users sometimes discover that nodes at a particular level of the navigation map correspond to classes of events in the search activity. Similarly, a characteristic structure accrues to pages that users return to frequently to follow other links. The fact that the interface creates structure that can be interpreted in this way may suggest new task decompositions to the user or may support alternative strategies for the allocation of effort in the activity. Distributed cognition encourages exploration of the tight coupling of interface components and cognition. Better understanding of this coupling may help in explaining why zoomable multiscale interfaces seem so compelling and assist in effective design of alternative multiscale representations. The integrated framework encourages us to augment experimental evaluation of Pad 11 with ethnographic analyses, not only of usage patterns, but also of the general navigation activities people exploit in dealing with emergent structure in dynamic information displays.

## 3.6 Intelligent Use of Space

In observing people's behavior in Pad 11 it is apparent that how they manipulate icons, objects, and emergent structure is not incidental to their cognition; it is part of their thinking process, part of the distributed process of achieving cognitive goals. They leave certain portals open to remind them of potentially useful information or to keep changes nicely visualized; they shift objects in size to emphasize their relative importance; and they move collections of things in and out of their primary workspace when they want to keep certain information around but have other concerns that are more pressing.

Studies of planning and activity have typically focused on the temporal ordering of action, but we think it is important to also explore questions about where agents lay down instruments, ingredients, work-in-progress, and the like. For in having a body, we are spatially located creatures: we must always be facing some direction, have only certain objects in view, be within reach of certain others. Whether we are aware of it or not, we are constantly organizing and reorganizing our workplace to enhance performance. Space is a resource that must be managed, much like time, memory, and energy. Accordingly we predicted that when space is used well it reduces the time and memory demands of our tasks, and increases the reliability of execution and the number of jobs we can handle at once.

In Kirsh [1995] we classified the functions of space into three main categories: spatial arrangements that simplify choice, spatial arrangements

•

that simplify perception, and spatial dynamics that simplify internal computation. The data for such a classification was drawn from videos of cooking, assembly, and packing, from everyday observations in supermarkets, workshops, and playrooms, and from experimental studies of subjects playing Tetris, the computer game. The studies, therefore, focused on interactive processes in the medium and short term: on how agents set up their workplace for particular tasks, and how they continuously manage that workplace.

As with many such studies it is not easy to summarize our findings, though our main conjecture was strongly confirmed. In several environments we found subjects using space to simplify choice by creating arrangements that served as heuristic cues. For instance, we saw them covering things, such as garbage disposal units or hot handles, thereby hiding certain affordances or signaling a warning and so constraining what would be seen as feasible. At other times they would highlight affordances by putting items needing immediate attention near to them, or creating piles that had to be dealt with. We saw them lay down items for assembly in a way that was unambiguously encoding the order in which they were to be put together or handed off. That is, they were using space to encode ordering information and so were off-loading memory. These are just a few of the techniques we saw them use to make their decision problems combinatorially less complex.

We also found subjects reorganizing their workspace to facilitate perception: to make it possible to notice properties or categories that were not noticed before, to make it easier to find relevant items, to make it easier for the visual system to track items. One subject explained how his father taught him to place the various pieces of his dismantled bicycle, many of which were small, on a sheet of newspaper. This made the small pieces easier to locate and less likely to be kicked about. In videos of cooking we found chefs distinguishing otherwise identical spoons by placing them beside key ingredients or on the lids of their respective saucepans, thereby using their positions to differentiate or mark them. We found jigsaw puzzlers grouping similar pieces together, thereby exploiting the capacity of the visual system to note finer differences between pieces when surrounded by similar pieces than when surrounded by different pieces.

Finally, we found a host of ways that embodied agents enlist the world to perform computation for them. Familiar examples of such off-loading show up in analog computations. When the tallest spaghetti noodle is singled out from its neighbors by striking the bundle on a table, a sort computation is performed by using the material and spatial properties of the world. But more prosaically we have found in laboratory studies of the computer game Tetris that players physically manipulate forms to save themselves computational effort [Kirsh 2001; Kirsh and Maglio 1995]. They modify the environment to cue recall, to speed up identification, and to generate mental images faster than they could if unaided. In short, they make changes to the world to save themselves costly and potentially error-prone computations.

All the work we have discussed above points to one fact: people form a tightly coupled system with their environments. The environment is one's partner or cognitive ally in the struggle to control activity. Although most of us are unaware of it, we constantly create external scaffolding to simplify our cognitive tasks. Helpful workflow analyses must focus on how, when, and why this external scaffolding is created. We think an integrated research environment such as we propose is absolutely crucial to such analyses and as foundation for creating digital environments which make these cognitive alliances as powerful as possible.

## 4. CONCLUSIONS AND FUTURE DIRECTIONS

Human-computer interaction as a field began at a time in which human information processing psychology was the dominant theory and still reflects that lineage. The human information processing approach explicitly took an early conception of the digital computer as the primary metaphorical resource for thinking about cognition. Just as it focused on identifying the characteristics of individual cognition, human-computer interaction, until very recently, has focused almost exclusively on single individuals interacting with applications derived from decompositions of work activities into individual tasks. This theoretical approach has dominated human-computer interaction for over 20 years, playing a significant role in developing a computing infrastructure built around the personal computer and based on the desktop interface metaphor.

For human-computer interaction to advance in the new millennium we need to better understand the emerging dynamic of interaction in which the focus task is no longer confined to the desktop but reaches into a complex networked world of information and computer-mediated interactions. A central image for us is that of future work environments in which people pursue their goals in collaboration with elements of the social and material world. We think that to accomplish this will require a new theoretical basis and an integrated framework for research.

Here we propose distributed cognition as a theoretical foundation for human-computer interaction research. Distributed cognition, developed over the past 12 years, is specifically tailored to understanding interactions among people and technology. The central hypothesis is that the cognitive and computational properties of systems can be accounted for in terms of the organization and propagation of constraints. This theoretical characterization attempts to free research from the particulars of specific cases but still capture important constituents of interactions among people and between people and material artifacts.

Taking a distributed cognition perspective radically alters the way we look at human-computer interaction. In the traditional view, something special happens at the boundary of the individual cognitive system. Traditional information processing psychology posits a gulf between inside and outside and then 'bridges' this gulf with transduction processes that convert external events into internal symbolic representations. The impli-

•

cation of this for HCI is that the computer and its interface are 'outside' of cognition and are only brought inside through symbolic transduction (see Card et al. [1983]). Distributed cognition does not posit a gulf between 'cognitive' processes and an 'external' world, so it does not attempt to show how such a gulf could be bridged. Moving the boundary of the unit of cognitive analysis out allows us to see that other things are happening there. Cognitive processes extend across the traditional boundaries as various kinds of coordination are established and maintained between 'internal' and 'external' resources. Symbolic transduction is only one of myriad forms of coordination that may develop between a user and a feature of a computer system.

We propose an integrated framework for research that combines ethnographic observation and controlled experimentation as a basis for theoretically informed design of digital work materials and collaborative workplaces. The framework makes a deep commitment to the importance of observation of human activity 'in the wild' and analysis of distributions of cognitive processes. In particular it suggests we focus on distributions of cognitive processes across members of social groups, coordination between internal and external structure, and how products of earlier events can transform the nature of later events.

This integrated approach strongly suggests that human-computer interaction research should begin in ethnographic studies of the phenomena of interest and with natural histories of the representations employed by practitioners. This in turn suggests that researchers must have a deeper understanding of the domains involved in order to, among other things, allow them to act as participant observers as well as to be theoretically and methodologically positioned to see existing functional organizations. The framework we propose holds that grounding in cognitive ethnography and integration of ethnographic methods with normal experimental analysis is fundamental to effective iterative evolution of interfaces. This framework also suggests that there are important opportunities available for designing and building systems that capture and exploit histories of usage. Such histories can not only be the basis for assisting users but also, with privacy concerns adequately addressed, provide researchers and developers with crucially important continuing data streams to assist future development.

As we mentioned earlier, the integrated research program described in this article does not yet exist. We realize that it is quite ambitious in scope and in the skills demanded. The issues to be addressed are complex. Strategic advances will require considerable coordination of research activities on a scale not now associated with the field of human-computer interaction. In addition, graduate training programs will need to be expanded to incorporate training in a wider array of research skills. As a step in that direction, we have recently joined together to form a new research laboratory, Distributed Cognition and Human-Computer Interaction Laboratory, and are designing a graduate education and research training program for human-computer interaction based on the theory of distributed cognition. As part of that effort we are embarking on a research enterprise

•

[Hollan et al. 1998] coordinated by the integrated framework we have described. We will need to await the results of these ventures to better understand the consequences of putting into practice what we propose. Still, we hope it is clear that without theories that view human-computer interaction within larger sociotechnical contexts and without a theoretically based research framework that integrates ethnographic and experimental approaches, it is unlikely the field of human-computer interaction will do justice to designing the intellectual workplaces of the future and ensuring that they meet human needs.

## ACKNOWLEDGMENTS

The development of this article has benefited from many discussions with members of our research group: Dan Bauer, Aaron Cicourel, Ian Fasel, Deborah Forster, David Fox, Mike Hayward, Jonathan Helfman, Ron Hightower, Barbara Holder, Sam Horodezky, Terry Jones, Todd Kaprielian, Tim Marks, Jonathan Nelson, Thomas Rebotier, Ron Stanonik, Scott Stornetta, and Peg Syverson.

## REFERENCES

AGAR, M. 1986. Speaking of Ethnography . Sage Publications, Inc., Thousand Oaks, CA.

- BEDERSON, B. B. AND HOLLAN, J. D. 1994. Pad 11 : A zooming graphical interface for exploring alternate interface physics. In Proceedings of the 7th Annual ACM Symposium on User Interface Software and Technology (UIST '94, Marina del Rey, CA, Nov. 2-4), P. Szekely, Ed. ACM Press, New York, NY, 17-26.
- BEDERSON, B. B., HOLLAN, J. D., PERLIN, K., MEYER, J., BACON, D., AND FURNAS, G. 1996. Pad 11 : A zoomable graphical sketchpad for exploring alternate interface physics. J. Visual Lang. Comput. 7 , 3-31.
- BROOKS, R. A. 1991. Intelligence without reason. In Proceedings of the 12th International Joint Conference on Artificial Intelligence (Sydney, Australia, Aug.), R. Myopoulos and J. Reiter, Eds. Morgan Kaufmann, San Mateo, CA, 569-595.
- CARD, S. K., MORAN, T. P., AND NEWELL, A. 1983. The Psychology of Human-Computer Interaction . Lawrence Erlbaum Assoc. Inc., Hillsdale, NJ.
- CLARK, A. 1997. Being There: Putting Brain, Body, and World Together Again . MIT Press, Cambridge, MA.
- COLE, M. 1996. Cultural Psychology . Harvard University Press, Cambridge, MA.
- EICK, S. G., STEFFEN, J. L., AND SUMNER, E. E. 1992. Seesoft-a tool for visualizing line oriented software statistics. IEEE Trans. Softw. Eng. 18 , 11 (Nov. 1992), 957-968.
- GOODWIN, C. AND GOODWIN, M. H. 1996. Formulating planes: Seeing as situated activity. In Cognition and Communication at Work , Y. Engeström and D. Middleton, Eds. Cambridge University Press, New York, NY.
- GRAS, A., MORICOT, C., POIROT-DELPECH, S., AND SCARDIGLI, V. 1991. Le pilote, le controleur, et l'automate. Tech. Rep.. Reedition du rapport predefinition pirttem-cnrs et du rapport final sert-ministere des transports. ed.
- HALVERSON, C. A. 1995. Inside the cognitive workplace: Air traffic control automation. Ph.D. Dissertation. Department of Cognitive Science, University of California, San Diego, CA.
- HAZELHURST, B. 1994. Fishing for cognition. Ph.D. Dissertation. Department of Cognitive Science, University of California, San Diego, CA.
- HIGHTOWER, R. R., RING, L. T., HELFMAN, J. I., BEDERSON, B. B., AND HOLLAN, J. D. 1998. Graphical multiscale Web histories: a study of padprints. In Proceedings of the 9th ACM Conference on Hypertext and Hypermedia: Links, Objects, Time and Space-Structure in
- ACM Transactions on Computer-Human Interaction, Vol. 7, No. 2, June 2000.

•

- Hypermedia Systems (HYPERTEXT '98, Pittsburgh, PA, June 20-24), R. Akscyn, Ed. ACM Press, New York, NY, 58-65.
- HILL, W. C. AND HOLLAN, J. D. 1994. History-enriched digital objects: Prototypes and policy issues. Inf. Soc. 10 , 139-145.
- HILL, W. C., HOLLAN, J. D., WROBLEWSKI, D., AND MCCANDLESS, T. 1992. Edit wear and read wear. In Proceedings of the ACM Conference on Human Factors in Computing Systems (CHI '92, Monterey, CA, May 3-7), P. Bauersfeld, J. Bennett, and G. Lynch, Eds. ACM Press, New York, NY, 3-9.
- HOLLAN, J. AND STORNETTA, S. 1992. Beyond being there. In Proceedings of the ACM Conference on Human Factors in Computing Systems (CHI '92, Monterey, CA, May 3-7), P. Bauersfeld, J. Bennett, and G. Lynch, Eds. ACM Press, New York, NY, 119-125.
- HOLLAN, J. D., BEDERSON, B. B., AND HELFMAN, J. 1997. Information visualization. In Handbook of Human-Computer Interaction , M. G. Helander, T. K. Landauer, and V. Prabhu, Eds. Elsevier Science Publishers Ltd., Essex, UK, 33-48.
- HOLLAN, J., HUTCHINS, E., AND WEITZMAN, L. 1984. STEAMER: An interactive inspectable simulation-based training system. AI Mag. 5 , 2, 15-27.
- HOLLAN, J. D., HUTCHINS, E. L., AND KIRSCH, D. 1998. KDI: A distributed cognition approach to designing digital work materials for collaborative workplaces. http://www.nsf.gov/ cgi-bin/showaward?award 5 9873156.
- HUTCHINS, E. 1980. Culture and Inference . Harvard University Press, Cambridge, MA.
- HUTCHINS, E. 1994. Cognition in the Wild . MIT Press, Cambridge, MA.
- HUTCHINS, E. L. 1995. How a cockpit remembers its speed. Cogn. Sci. 19 , 265-288.
- HUTCHINS, E. L. 1996. The integrated mode management interface. Tech. Rep. University of California at San Diego, La Jolla, CA. Final report for project NCC 92-578, NASA Ames Research Center)
- HUTCHINS, E. L. AND KLAUSEN, T. 1996. Distributed cognition in an airline cockpit. In Cognition and Communication at Work , Y. Engeström and D. Middleton, Eds. Cambridge University Press, New York, NY, 15-34.
- HUTCHINS, E. L. AND PALEN, L. 1997. Constructing meaning from space, gesture, and speech. In Tools, and Reasoning: Essays in Situated Cognition , L. B. Resneck, R. Saljo, C. Pontecorvo, and B. Burge, Eds. Springer-Verlag, Vienna, Austria.
- HUTCHINS, E. L., HOLLAN, J. D., AND NORMAN, D. A. 1985. Direct manipulation interfaces. Human-Comput. Interact. 1 , 4, 311-338.
- KIRSH, D. 1995. The intelligent use of space. Artif. Intell. 73 , 1-2 (Feb. 1995), 31-68.
- KIRSH, D. 1996. Adapting the environment instead of oneself. Adapt. Behav. 4 , 3-4, 415-452.
- KIRSH, D. 2001. Are all actions exploratory or performatory?. Ecol. Psychol. 13 .
- KIRSH, D. AND MAGLIO, P. 1994. On distinguishing epistemic from pragmatic action. Cogn. Sci. 18 , 4, 513-549.
- KRONENFELD, D. 1996. Plastic Glasses and Church Fathers . Oxford University Press, Oxford, UK.
- LAKOFF, G. 1987. Women, Fire, and Dangerous Things: What Categories Reveal about the Mind . University of Chicago Press, Chicago, IL.
- MATURANA, H. AND VARELLA, F. 1987. The Tree of Knowledge: The Biological Roots of Human Understanding . New Science Library.
- MINSKY, M. 1986. The Society of Mind . Simon &amp; Schuster, Inc., New York, NY.
- NORMAN, D. A. 1993. Things That Make Us Smart: Defending Human Attributes in the Age of the Machine . Addison-Wesley Longman Publ. Co., Inc., Reading, MA.
- ROBERTS, J. 1964. The self-management of culture. In Explorations in Cultural Anthropology: Essays in Honor of George Peter Murdoc , W. Goodenough, Ed. McGraw-Hill, London, UK.
- SALOMAN, G., Ed. 1993. Distributed Cognitions: Psychological and Educational Considerations. Learning in Doing: Social, Cognitive, and Computational Perspectives . Cambridge University Press, New York, NY.
- SEIFERT, C. M. AND HUTCHINS, E. L. 1992. Error as opportunity: Learning in a cooperative task. Hum. Comput. Interact. 7 .
- SHORE, B. 1996. Culture in Mind . Oxford University Press, Oxford, UK.

•

- STRAUSS, C. AND QUINN, N. 1998. A Cognitive Theory of Cultural Meaning . Cambridge University Press, New York, NY.
- SUCHMAN, L. A. 1987. Plans and Situated Actions: The Problem of Human-Machine Communication . Cambridge University Press, New York, NY.
- THELEN, E. 1995. Timescale dynamics and the development of an embodied cognition. In Mind as Motion: Explorations in the Dynamics of Cognition , R. F. Port and T. van Gelder, Eds. Massachusetts Institute of Technology, Cambridge, MA.
- TURVEY, M., SHAW, R., REED, E., AND MACE, W. 1981. Ecological laws of perceiving and acting. Cognition 9 , 238-304.
- TYLER, S. 1969. Cognitive Anthropology . Holt, Rinehart and Winston, Austin, TX.
- VARLEA, F., THOMPSON, E., AND ROSCH, E. 1991. The Embodied Mind . MIT Press, Cambridge, MA.
- WALLACE, A. 1970. Cultural and Cognition . Random House Inc., New York, NY.
- WERNER, O. AND SCHOEPFLE, M. 1987. Systematic Fieldwork . Sage Publications, Inc., Thousand Oaks, CA.

Received: February 1999; revised: April 2000; accepted: April 2000
