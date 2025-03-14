import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Circle
import matplotlib.patheffects as pe
import matplotlib.lines as mlines


def simplify(input_array:np.ndarray[int]):
    """checks if all inputs can be divided by either 2 or 3 and simplifies"""
    dividing = True
    while dividing:
        if (input_array % 2 == 0).all():
            input_array = input_array // 2
        elif (input_array % 3 == 0).all():
            input_array = input_array // 3
        else:
            dividing = False
    return input_array

def divisable_3(number:int):
    """returns true if number is divisible by 3"""
    return number % 3 == 0

def divisable_2(number:int):
    """returns true if number is divisible by 2"""
    return number % 2 == 0

def calculate_return(total):
    """Returns if the layer needs a return output"""
    if divisable_3(total) or divisable_2(total):
        return 0
    else:
        return 1


def calculate_splitter_fraction(input_array:np.ndarray[int], total = None):
    """takes the simplified inputs for a layer and returns the splitter used, the total output, and if there is a return output"""

    if total is None:
        total = input_array.sum()  # sets the total as the sum of the input for the first layer

    layer_return = calculate_return(total)
    total += layer_return  # adds the return output to the total if a return is needed
    # the return layers should be considered part of the total output which is why total needs to be returned and is
    # only set as a sum of the inputs at the start.

    if divisable_3(total):
        return 3, total, layer_return  # returns the splitter used, the total outputs, and if there is a return in this layer
    else:
        return 2, total, layer_return

def calculate_splitters(input_array:np.ndarray[int]):
    """
    This is the main function that solves the splitter problem
    inputs: a numpy array with the desired outputs of the splitter

    returns: a list of "splits" which contains the output of the calculate_splitter_fraction function and an array of
            how many outputs per layer are taken by every output
    """

    input_array.sort()  # sorts the input from smallest to largest
    input_array = input_array[::-1]  # reverses the input array to largest to smallest
    input_array = simplify(input_array)  # checks if the inputs have common denominator of 2 or 3 and simplifies
    splits = list()  # initialise the list of splits which will be the output
    splitting = True
    total = None

    while splitting:  # loop over the layers

        split = list(calculate_splitter_fraction(input_array, total=total))  # gets the split for the current layer
        takes = input_array % split[0]  # checks if an output of the current layer can be taken entirely by one of the outputs
        splits.append(list((split,takes)))  # store split and takes in the splits list

        total = split[1]  # get the total from the split
        total = total // split[0]  # divide the split by the splitter size
        if split[1]<=3: # check if the trivial solution is found
            splitting = False
        else:
            input_array = input_array//split[0]  # divide out the outputs that were "taken" in the take array to keep
                                                 # track of how many outputs are still needed
    splits = list(splits)  # cast splits into a list
    splits = splits[::-1]  # get the reverse order of the splits list

    return splits

def visualise_layers(splits):
    """Visualise the splits"""

    fig = plt.gcf()  # get the current figure
    ax = plt.gca()  # get the current axis

    outputs = splits[0][1].shape[0]  # get the number of outputs
    available_splits = 1  # initialise the number of available splits (1 for 1 input)
    total_split = 1  # keep track of the total split meaning one output of a splitter is 1/total_split of the input
    y_max = 0  # keep track of what the lowes y position will be on the plot
    total_return = 0  # how much of the total has been returned
    first_layer = np.zeros(outputs)  # keep track of what the first layer was for each output (used as a start for the vertical line)

    nr_rows = len(splits) + 1  # get the number of rows, used for scaling
    circle_radius = 0.075*(outputs)  # set the radius of the circles to indicate splitter positions

    # checks if any of the rows has a return value
    returns = False
    for split in splits:
        if split[0][2] > 1:
            returns = True

    # get the width of the image
    if returns:
        im_width = outputs + 3
    else:
        im_width = outputs + 1

    # loop over the splits and draw the outputs of the splitters
    for i, split in enumerate(splits):
        splitter_size = split[0][0]  # get the size of the current splitter
        top_interval = im_width/(total_split+1)  # get the spacing of the top row between the splitters

        total_split *= splitter_size  # keep track of the fraction of the total split
        total_return *= splitter_size  # keep track of how much is returned
        available_splits *= splitter_size  # get the number of available splits

        bottom_interval = im_width/(total_split+1)  # get the spacing of the bottom row between the splitters
        splits_taken = split[1].sum()

        for k, num in enumerate(split[1]):
            # draw the splits connecting to the outputs
            # num is the number of outputs of the splitters connected to one of the outputs
            first = False
            if first_layer[k] == 0 and num>0:
                # keep track of the first layer where an output is outputted to
                first_layer[k] = i+1
                first = True  # keep track of the first time an output is drawn as this does not require a merger

            for l in range(num):  # loop over the total number of outputs of the splitters that go to the output corresponding to k

                j = total_split - total_return - available_splits # j corresponds to the index of the splitter output where j can range from 0 to total_split
                splitter_x_pos = top_interval * (1+j // splitter_size)  # get the x position of the splitter

                if l%3 == 1 and splitter_size == 3:  # draw a small vertical line before connecting to the output for clarity
                    plt.plot([splitter_x_pos, splitter_x_pos],[i,i+0.5], "blue")  # small vertical line
                    plt.plot([splitter_x_pos, k + 1], [i+0.5, i + 1], "blue")  # line connecting to the output
                else:
                    plt.plot([splitter_x_pos,k+1],[i,i+1], "blue") # line connecting to the output
                available_splits -=1  # subtract the splitter output that was connected to the output from available splits

                if y_max < i+1:
                    y_max = i+1  # keep track of the lowest point

            if num > 0 and not first:
                # draw the merger circle
                circle = Ellipse(
                    (k+1, i + 1),
                    circle_radius, (nr_rows+2) / outputs * circle_radius, color="red") # create the circle
                ax.add_patch(circle)  # add the circle to the image
                plt.text(k+1, i+1,
                     "merger", color="white", horizontalalignment="center", verticalalignment="center",
                     fontweight="bold", path_effects=[pe.withStroke(linewidth=1, foreground="black")])  # add merger text to the image


        for j in range(total_split-total_return - available_splits,total_split-total_return-split[0][2]):
            # draw the other forward splits
            plt.plot([top_interval*(1+j//splitter_size), bottom_interval*(1+j)],[i, i+1],color="blue")


        if split[0][2]>0:
            # draw return split if required
            j = total_split-total_return
            plt.plot([top_interval * (j // splitter_size), bottom_interval * (1 + j)], [i, i + 1], color="red")
            available_splits -= 1  # subtract the return from the available splits

        for j in range(available_splits):
            # draw the splitter circles on the row below
            circle = Ellipse((bottom_interval*((total_split-total_return-available_splits)+j+1-split[0][2]), i+1), circle_radius, (nr_rows+2)/outputs*circle_radius)
            ax.add_patch(circle)
            # add the size of the splitter
            plt.text(bottom_interval*((total_split-total_return-available_splits)+j+1-split[0][2]), i+1,
                     str(splits[i+1][0][0]), color="white", horizontalalignment="center", verticalalignment="center",
                     fontweight="bold", path_effects=[pe.withStroke(linewidth=1, foreground="black")])

        total_return += split[0][2] # add the return value to the total return

    for i, start in enumerate(first_layer):
        # draw the vertical lines for the output
        plt.plot([i+1,i+1],[start, y_max+1],color="blue")
        # add the output names at the bottom
        plt.text(i+1, y_max+1.25,
                 f"output {i+1}", color="black", horizontalalignment="center", verticalalignment="center",
                 fontweight="bold", path_effects=[pe.withStroke(linewidth=1, foreground="white")])

    # draw the input circle
    circle = Ellipse((im_width/2,0),
                     circle_radius, (nr_rows+2) / outputs * circle_radius, color="lightgreen")
    ax.add_patch(circle)
    # write the input text
    plt.text(im_width/2,0,
             "input", color="white", horizontalalignment="center", verticalalignment="center",
             fontweight="bold", path_effects=[pe.withStroke(linewidth=1, foreground="black")])

    # draw the arrow on the left for clarity
    plt.arrow(0.75,0,0,y_max+0.75, width=0.02, color="black")

    # add a blue and red line to the legend
    blue_line = mlines.Line2D([], [], color="blue", linestyle="-", linewidth=1, label = "feed-forward")
    red_line = mlines.Line2D([], [], color="red", linestyle="-", linewidth=1, label= "feed-back")
    leg = plt.legend(handles = [blue_line, red_line])

    # reverse the direction of the y-axis (to from top to bottom)
    plt.ylim((y_max+1.5,-0.5))

    # remove the numbers from the axes
    ax.set_yticks([])
    ax.set_xticks([])

    plt.title("Splitter Layout")
    fig.set_layout_engine("tight")
    plt.show()

while True:
    inputs = input("Enter Required outputs comma separated (eg: 54,18,24) : ")
    inputs = inputs.split(",")
    inputs = np.array([int(input) for input in inputs])
    splitters = calculate_splitters(inputs)
    visualise_layers(splitters)