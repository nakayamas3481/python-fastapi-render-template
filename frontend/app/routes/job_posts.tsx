import { Link } from "react-router";
import { Button } from "~/components/ui/button";

export async function clientLoader({params}) {
  const res = await fetch(`/api/job-boards/${params.jobBoardId}/job-posts`);
  const jobPosts = await res.json();
  return {jobBoardId: params.jobBoardId, jobPosts}
}

export default function JobPosts({loaderData}) {
  const {jobBoardId, jobPosts} = loaderData;
  return (
    <div>
      <div className="float-right">
        <Button>
          <Link to={`/job-boards/${jobBoardId}/add-job`}>Add New Job</Link>
        </Button>
      </div>
      <div className="space-y-8">
        {loaderData.jobPosts.map(
          (jobPost) =>
            <div>
                <h2 key={jobPost.id}>
                  <Link to={`/job-boards/${jobBoardId}/job-posts/${jobPost.id}`}>
                    {jobPost.title}
                  </Link>
                </h2> 
            </div>
          )
        }
      </div>      
    </div>
  )
}
