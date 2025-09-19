
export function Results(results) {
    return (
        <>
            {
                results.map((result) => (
                    <Result result={result} />
                ))
            }
        </>
    );
}