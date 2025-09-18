import styles from '@/style.module.css';
import { useState } from 'react';

export function SearchBar() {
    const [terms, setTerms] = useState('');

    function getResults(terms: string) {
        const host : string = 'http://server1/search';
        // Delimit search terms by spaces and remove special characters
        const search_terms : string = terms
            .replace(' ', '+')
            .replace('&', '');
        const num_results : string = '10'

        // Build the request url
        const request_url : string = host + '?q=' + search_terms + '&n=' + num_results;

        // Send the search request to the server
        fetch(request_url)
            .then((resp) => {return resp.json()})
            .then((results) => {
                results.array.forEach((e : object) => {
                    // TODO: create components for each result and add them to the DOM
                });
            });
    }

    return (
        <>
            <form onSubmit={(e) => {
                e.preventDefault();
                getResults(terms);
            }}>
                <input id='search_in' name='search_in' type='text' value={terms} onChange={e => setTerms(e.target.value)}/>
                <input id='submit' type='submit' />
            </form>
            <div id='results'>

            </div>
        </>
    );
}