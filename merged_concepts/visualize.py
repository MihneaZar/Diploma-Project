from readchar import readkey, key
import graphviz
import yaml
import os


YES = "Yes"
NO  = "No"
def yes_or_no(question, default_answer=YES, newline=True):
    if newline:
        print(f'{question}\nY/N', flush=True)
    else: 
        print(f'{question} (Y/N): ', end='', flush=True)

    default_answer = default_answer.capitalize()
    answer = readkey().lower()
    while not answer in ['y', 'n']:
        if answer == key.ENTER:
            print(default_answer)
            if newline:
                print()
            return default_answer
        
        answer = readkey().lower()

    
    answer = YES if answer == 'y' else NO
    print(answer)
    if newline:
        print()
        
    return answer


def main():
    filename = input("Filename: ")
    try:
        data = yaml.safe_load(open(f'{filename}/{filename}.yaml'))
    except:
        print("No file with that name.")
        return
    
    treshhold = input("Connection tresshold: ")
    if not treshhold:
        treshhold = "0"
    try:
        treshhold = float(treshhold)
        assert(0 <= treshhold and treshhold <= 1)
    except:
        print("Treshhold must be a rational number between 0 and 1.")
        return
    
    change_direction = (yes_or_no("Change direction", NO, False) == YES)

    # non-normalized
    dot = graphviz.Digraph(name=f"{filename}")
    if change_direction:
        dot.graph_attr['rankdir'] = 'LR'  
    
    for el in data:
        dot.node(el, f'{el}\nyear: {data[el]["year"]}\ncount: {data[el]["count"]}\nnovelty: {(data[el]["recent"] / 5) / (data[el]["count"] / (2018 - data[el]["year"])):.2f}')

        for oth_el in data[el]["cooc"]:
            total_weight = sum([data[el]["cooc"][oth_el] for oth_el in data[el]["cooc"]])

            rel_val = data[el]["cooc"][oth_el]/total_weight
            if treshhold <= rel_val:
                dot.edge(el, oth_el, f'{rel_val:.2f}')

    dot.render(f"{filename}/{filename}", view=True)
    os.remove(f"{filename}/{filename}")

    # normalized
    dot = graphviz.Digraph(name=f"{filename}/{filename}_normalized")
    if change_direction:
        dot.graph_attr['rankdir'] = 'LR'  

    for el in data:
        dot.node(el, f'{el}\nyear: {data[el]["year"]}\ncount: {data[el]["count"]}\nnovelty: {(data[el]["recent"] / 5) / (data[el]["count"] / (2018 - data[el]["year"])):.2f}')

        total_weight  = sum([data[el]["cooc"][oth_el] for oth_el in data[el]["cooc"]])
        remove_weight = 0
        for oth_el in data[el]["cooc"]:
            if data[el]["cooc"][oth_el]/total_weight < treshhold:
                remove_weight += data[el]["cooc"][oth_el]
                data[el]["cooc"][oth_el] = 0
        
        total_weight -= remove_weight
        
        # all connections are weak
        if total_weight == 0:
            continue

        for oth_el in data[el]["cooc"]:
            if data[el]["cooc"][oth_el] != 0:
                dot.edge(el, oth_el, f'{data[el]["cooc"][oth_el]/total_weight:.2f}')
                
    dot.render(f"{filename}/{filename}_normalized", view=True)
    os.remove(f"{filename}/{filename}_normalized")


if __name__=="__main__":
    main()