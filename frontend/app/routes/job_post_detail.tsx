import { useState } from "react";
import { Button } from "~/components/ui/button";

export async function clientLoader({ params }) {
  const res = await fetch(`/api/job-posts/${params.jobPostId}`);
  if (!res.ok) {
    throw new Error("Failed to load job post");
  }
  const jobPost = await res.json();
  return { jobPost };
}

export default function JobPostDetail({ loaderData }) {
  const { jobPost } = loaderData;
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showApplicants, setShowApplicants] = useState(false);

  const handleApply = async () => {
    setShowApplicants(true);
  };

  const handleRecommendation = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/job-posts/${jobPost.id}/recommend`);
      if (res.ok) {
        const data = await res.json();
        setRecommendation(data);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{jobPost.title}</h1>
        <p className="mt-2">{jobPost.description}</p>
      </div>

      <div>
        <Button onClick={handleApply}>Apply</Button>
      </div>

      {showApplicants && (
        <div>
        <h2 className="text-xl font-semibold">Applicants</h2>
        {jobPost.applicants && jobPost.applicants.length > 0 ? (
          <ul className="list-disc pl-5 space-y-2">
            {jobPost.applicants.map((applicant) => (
              <li key={applicant.id}>
                <div className="font-medium">
                  {applicant.firtst_name} {applicant.last_name}
                </div>
                <div className="text-sm text-gray-600">{applicant.email}</div>
                {applicant.resume_url && (
                  <a
                    className="text-blue-600 text-sm"
                    href={applicant.resume_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    履歴書を見る
                  </a>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p>No applicants yet.</p>
        )}
        </div>
      )}

      <div className="space-y-3">
        <Button onClick={handleRecommendation} disabled={loading}>
          {loading ? "Loading..." : "Get Recommendation"}
        </Button>
        {recommendation && (
          <div className="border rounded p-3">
            <div className="font-semibold">
              {recommendation.firtst_name} {recommendation.last_name}
            </div>
            <div className="text-sm text-gray-700">{recommendation.email}</div>
            {recommendation.resume_url && (
              <a
                className="text-blue-600 text-sm"
                href={recommendation.resume_url}
                target="_blank"
                rel="noreferrer"
              >
                推奨履歴書
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
