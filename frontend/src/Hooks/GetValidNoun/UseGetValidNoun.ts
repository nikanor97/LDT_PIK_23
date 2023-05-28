type useGetValidNounProps = {
    nounTypes: {
        type1: string;
        type2: string;
        type3: string;
    };
    number?: number | undefined;
};

const useGetValidNoun = (props: useGetValidNounProps) => {
    const number = props.number ? props.number : 0;
    const nounTypes = props.nounTypes;

    if (number % 100 >= 10 && number % 100 <= 20) return nounTypes.type3;
    if (number % 10 === 1) return nounTypes.type1;
    if (number % 10 === 2 || number % 10 === 3 || number % 10 === 4) return nounTypes.type2;
    return nounTypes.type3;
};

export default useGetValidNoun;
