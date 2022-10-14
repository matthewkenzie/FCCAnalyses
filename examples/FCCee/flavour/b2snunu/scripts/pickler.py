from config import train_var_lists

def run(input_files, output_file, vars_list):
    import uproot
    df = uproot.concatenate( [inf+":events" for inf in input_files], library="pd", how="zip", filter_name=vars_list )
    df.to_pickle(output_file)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Applies preselection cuts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', nargs="+", required=True, help='Select the input file(s).')
    parser.add_argument('--output', type=str, required=True, help='Select the output file.')
    parser.add_argument('--vars', type=str, required=True, help='Select the variables to keep, e.g "train_vars_vtx", "train_vars_stage2"')
    args = parser.parse_args()

    assert( args.vars in train_var_lists.keys() )

    run(args.input, args.output, vars_list=train_var_lists[args.vars])

if __name__ == '__main__':
    main()
