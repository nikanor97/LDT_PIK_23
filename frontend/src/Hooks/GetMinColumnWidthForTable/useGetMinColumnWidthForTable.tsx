import React from "react";

const useGetMinColumnWidthForTable = (title: string) => {
    const TitleMinLength = title.length * 10;
    const FiltersMinLength = 65;
    const minWidth = TitleMinLength + FiltersMinLength;
    return minWidth;
};

export default useGetMinColumnWidthForTable;
