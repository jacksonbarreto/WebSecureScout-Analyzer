import os
import re
from typing import List, Dict, Any

import pandas as pd

standard_countable_variable = 'url'


def load_data(filename: str) -> pd.DataFrame:
    """
    Given a file name, returns the pandas data frame containing the data in that file.
    The file is assumed to be located in the 'data' directory and have a '.csv' extension.

    Args:
        filename: A string representing the name of the csv file to load.

    Returns:
        A pandas dataframe containing the data in the specified csv file.
    """
    file_path = os.path.join('..', 'data', f'{filename}.csv')
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}")


def get_records_by_region(source_df: pd.DataFrame, region_column_name: str = 'region',
                          column_name_to_results_global: str = 'Global #') -> pd.DataFrame:
    """
    Group the data by a region column and count the number of records in each region.

    Args:
        source_df: A pandas dataframe containing the data to be grouped.
        region_column_name: A string representing the column name of the region to group by. Default is 'region'.
        column_name_to_results_global: A string representing the new name of the count column. Default is 'Global #'.

    Returns:
        A new pandas dataframe with a count of records for each unique region.

    """
    records_by_region = source_df.groupby([region_column_name]).count()
    records_by_region.rename(columns={standard_countable_variable: column_name_to_results_global}, inplace=True)
    return records_by_region


def convert_int_column_to_int_type(dataframe: pd.DataFrame) -> None:
    """
    Convert all columns ending in '#' in a pandas dataframe to integer type.

    Args:
        dataframe: A pandas dataframe to be converted.

    Returns:
        None
    """
    columns = dataframe.columns.values.tolist()
    for column_name in columns:
        match = re.search(r'#$', column_name)
        if match:
            dataframe[column_name] = dataframe[column_name].astype(int)


def create_total_row(dataframe: pd.DataFrame, column_name_to_results_global: str = 'Global #') -> None:
    """
    Add a total row to a pandas dataframe and calculate percentages for columns ending in '%'.

    Args:
        dataframe: A pandas dataframe to add the total row to.
        column_name_to_results_global: The name of the column containing the total number of results.
        Default is 'Global #'.

    Returns:
        None
    """
    columns = dataframe.columns.values.tolist()
    dataframe.loc['Total'] = dataframe.sum()
    for column_name in columns:
        match = re.search(r'%$', column_name)
        if match:
            integer_column = column_name[:-1] + '#'
            total_count = dataframe.loc['Total', column_name_to_results_global]
            column_sum = dataframe.loc['Total', integer_column]
            dataframe.loc['Total', column_name] = column_sum / total_count * 100


def sort_results_by_indicator(dataframe: pd.DataFrame, column: str, ascending: bool = True) -> None:
    """
    Sorts a pandas DataFrame by a specified column in ascending or descending order.

    Args:
        dataframe: The DataFrame to sort.
        column: The column to sort by.
        ascending: Whether to sort in ascending (True) or descending (False) order. Defaults to True.
    """
    dataframe.sort_values(by=column, ascending=ascending, inplace=True)


def create_percent_column(dataframe: pd.DataFrame, integer_column: str,
                          column_name_to_results_global: str = 'Global #') -> None:
    """
    Creates a new column in a pandas DataFrame representing the percentage of a given integer column
    relative to a specified global column.

    Args:
        dataframe: The DataFrame to operate on.
        integer_column: The name of the integer column to calculate the percentage of.
        column_name_to_results_global: The name of the global column representing the total count of results.
            Defaults to 'Global #'.
    """
    percent_column = integer_column[:-1] + '%'
    dataframe[integer_column] = dataframe[integer_column].fillna(0)
    dataframe[percent_column] = dataframe[integer_column] / dataframe[column_name_to_results_global] * 100


def validate_row_percent(dataframe: pd.DataFrame) -> None:
    """
    Validates that the sum of percentage columns in each row of a pandas DataFrame is equal to 100.

    Args:
        dataframe: The pandas DataFrame to validate.

    Raises:
        ValueError: If the sum of percentage columns in a row is not equal to 100.
    """
    columns = dataframe.columns.values.tolist()
    for index, row in dataframe.iterrows():
        percent_sum = 0
        for column_name in columns:
            match = re.search(r'%$', column_name)
            if match:
                percent_sum += row[column_name]
        if abs(percent_sum - 100) > 0.00001:
            raise ValueError(f"Percent sum is not equal to 100 for row {index}: {percent_sum}")


def create_column(source_df: pd.DataFrame, analysis_dataframe: pd.DataFrame, column_name: str, criteria: str,
                  columns_to_display: list[str], region_column_name: str = 'region') -> list[str]:
    """
    Creates a new column in the analysis dataframe based on the criteria specified in the source dataframe.

    Args:
        source_df: The source dataframe containing the data to be analyzed.
        analysis_dataframe: The dataframe to add the new column to.
        column_name: The name of the new column to add to the analysis dataframe.
        criteria: A list of strings representing the criteria to add to the new column.
        region_column_name: The name of the region column in the source dataframe. Default is 'region'.
        columns_to_display: A list of column names to display.
    """
    column_name_integer = f'{column_name} #'
    column_name_percent = f'{column_name} %'
    analysis_dataframe[column_name_integer] = source_df.query(criteria).groupby([region_column_name]).count()[
        standard_countable_variable]
    create_percent_column(analysis_dataframe, column_name_integer)
    columns_to_display.extend([column_name_integer, column_name_percent])
    return columns_to_display


def finalize_dataframe(dataframe: pd.DataFrame, columns_to_display: list[str], column_to_sort: str,
                       ascending: bool = True) -> pd.DataFrame:
    """
    Finalizes a pandas DataFrame by converting integer columns to integer type, adding a total row,
    sorting the DataFrame, and creating percentage columns.

    Args:
        dataframe: The DataFrame to finalize.
        columns_to_display: A list of column names to display.
        column_to_sort: The name of the column to sort by.
        ascending: Whether to sort in ascending (True) or descending (False) order. Defaults to True.

    Returns:
        The finalized DataFrame.
    """
    sort_results_by_indicator(dataframe, column_to_sort, ascending)
    create_total_row(dataframe)
    convert_int_column_to_int_type(dataframe)
    # makes the current index (region) back to a number and the region column back to a column again
    dataframe.reset_index(inplace=True)
    # Transforms all column names to title style
    dataframe.columns = dataframe.columns.str.title()
    # Transforms all column names in columns_to_display to title style
    columns_to_display = [column.title() for column in columns_to_display]
    dataframe = dataframe[columns_to_display]
    validate_row_percent(dataframe)
    return dataframe


def get_extreme_values(data: pd.DataFrame, columns: List[str] = None) -> dict[str | Any, dict[str, list[Any]] | dict]:
    """
    Returns a dictionary with the column name as key and a list of the 3 largest and 3 smallest column values as value.

    Args:
        data: A pandas dataframe.
        columns: A list of column names to consider.

    Returns:
        A dictionary with the column name as key and a list of the 3 largest and 3 smallest column values as value.
    """
    result = {}
    total_row = data.tail(1)

    if columns is None:
        columns = data.columns.values.tolist()
        columns.remove('Region')

    data = data.drop(data.tail(1).index)
    for column in columns:
        top_regions = data[['Region', column]].sort_values(by=column, ascending=False).head(3).to_records(index=False)
        bottom_regions = data[['Region', column]].sort_values(by=column, ascending=True).head(3).to_records(index=False)
        result[column] = {'top_regions': list(top_regions), 'bottom_regions': list(bottom_regions)}

    result['Total'] = {col: total_row[col].values[0] for col in columns}
    return result


def save_string_to_file(file_name: str, string: str) -> None:
    """
    Saves a string to a file.

    Args:
        file_name: The name of the file to save to.
        string: The string to save.
    """
    with open(file_name.lower(), 'w') as file:
        file.write(string)


def create_directory_structure() -> None:
    """
    Creates the directory structure for the output files.
    """
    main_dir = '../analyzes'
    sub_dir = ['tables', 'reports']
    categories_dir = ['security_headers', 'dnssec', 'https', 'security_layer', 'population']
    for sub_directory in sub_dir:
        for category in categories_dir:
            os.makedirs(os.path.join(main_dir, sub_directory, category), exist_ok=True)


def save_dataframe_to_csv(dataframe: pd.DataFrame, file_name: str) -> None:
    """
    Saves a pandas DataFrame to a CSV file.

    Args:
        dataframe: The DataFrame to save.
        file_name: The name of the file to save to.
    """
    dataframe.to_csv(file_name.lower(), index=False)


def save_table(dataframe: pd.DataFrame, category: str, table_name: str) -> None:
    """
    Saves a pandas DataFrame to a CSV file.

    Args:
        dataframe: The DataFrame to save.
        category: The category of the table.
        table_name: The name of the table.
    """
    file_name = f'../analyzes/tables/{category}/{table_name}.csv'
    save_dataframe_to_csv(dataframe, file_name)


def save_report(report: str, category: str, report_name: str) -> None:
    """
    Saves a pandas DataFrame to a CSV file.

    Args:
        report: The report to save.
        category: The category of the report.
        report_name: The name of the report.
    """
    file_name = f'../analyzes/reports/{category}/{report_name}.txt'
    save_string_to_file(file_name, report)
