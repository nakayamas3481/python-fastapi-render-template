import { Link } from "react-router";

export default function Home({}) {
    console.log("Hello")
    return (
        <main>
            <h1 className="text-3xl font-medium">Welcome to Jobify </h1>
            <p className="mt-4">Your search for your next job stop here! </p>
        </main>
    )
}